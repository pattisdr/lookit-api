import json
import uuid
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from guardian.shortcuts import assign_perm
from studies.models import Response, Study, Feedback
from accounts.models import Child, User, DemographicData
from django_dynamic_fixture import G


class ResponseTestCase(APITestCase):
    def setUp(self):
        self.researcher = G(User, is_active=True, is_researcher=True, given_name="Researcher 1")
        self.participant = G(User, is_active=True, given_name="Participant 1")
        self.demographics = G(DemographicData, user=self.participant, languages_spoken_at_home="French")
        self.participant.save()

        self.child = G(Child, user=self.participant, given_name='Sally')
        self.child2 = G(Child, user=self.researcher, given_name='Grace')
        self.study = G(Study, creator=self.researcher)
        self.response = G(Response, child=self.child, study=self.study, completed=False)
        self.url = reverse('response-list',  kwargs={'version':'v1'})
        self.response_detail_url = self.url + str(self.response.uuid) + '/'
        self.client = APIClient()

        self.data = {
            "data": {
                "attributes": {
                  "global-event-timings": [],
                  "exp-data": {},
                  "sequence": [],
                  "completed": False
                },
                "relationships": {
                  "child": {
                    "data": {
                      "type": "children",
                      "id": str(self.child.uuid)
                    }
                  },
                  "study": {
                    "data": {
                      "type": "studies",
                      "id": str(self.study.uuid)
                    }
                  }
                },
                "type": "responses"
            }
        }
        self.patch_data = {
            "data": {
                "attributes": {
                  "global-event-timings": [],
                  "exp-data": {"some":"data"},
                  "sequence": ['first_frame', 'second_frame'],
                  "completed": True
                },
                "type": "responses",
                "id": str(self.response.uuid)
            }
        }



    # Response List test
    def testGetResponseListUnauthenticated(self):
        #  Must be authenticated to view participants
        api_response = self.client.get(self.url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testGetResponsesListByOwnChildren(self):
        # Participant can view their own responses
        self.client.force_authenticate(user=self.participant)
        api_response = self.client.get(self.url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['links']['meta']['count'], 1)

    def testGetResponsesListViewStudyPermissions(self):
        # Can view study permissions insufficient to view responses
        assign_perm('studies.can_view_study', self.researcher, self.study)
        self.client.force_authenticate(user=self.researcher)
        api_response = self.client.get(self.url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['links']['meta']['count'], 0)

    def testGetResponsesListViewStudyResponsesPermissions(self):
        # With can_view_study_responses permissions, can view study responses
        assign_perm('studies.can_view_study_responses', self.researcher, self.study)
        self.client.force_authenticate(user=self.researcher)
        api_response = self.client.get(self.url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['links']['meta']['count'], 1)

    # Response Detail tests
    def testGetResponseDetailUnauthenticated(self):
        # Can't view response detail unless authenticated
        api_response = self.client.get(self.response_detail_url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testGetResponseDetailByOwnChildren(self):
        # Participant can view their own response detail
        self.client.force_authenticate(user=self.participant)
        api_response = self.client.get(self.response_detail_url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['completed'], False)

    def testGetResponseDetailViewStudyPermissions(self):
        # Can view study permissions insufficient to view responses
        assign_perm('studies.can_view_study', self.researcher, self.study)
        self.client.force_authenticate(user=self.researcher)
        api_response = self.client.get(self.response_detail_url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_404_NOT_FOUND)

    def testGetResponseDetailViewStudyResponsesPermissions(self):
        # With can_view_study_responses permissions, can view study response detail
        assign_perm('studies.can_view_study_responses', self.researcher, self.study)
        self.client.force_authenticate(user=self.researcher)
        api_response = self.client.get(self.response_detail_url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['completed'], False)

    # POST Responses tests
    def testPostResponse(self):
        self.client.force_authenticate(user=self.participant)
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(api_response.data['completed'], False)
        self.assertEqual(Response.objects.count(), 2)

    def testPostResponseWithNotYourChild(self):
        self.client.force_authenticate(user=self.participant)
        self.data['data']['relationships']['child']['data']['id'] = str(self.child2.uuid)
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_403_FORBIDDEN)

    def testPostResponseNeedDataHeader(self):
        self.client.force_authenticate(user=self.participant)
        data = {}
        api_response = self.client.post(self.url, json.dumps(data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual( api_response.data['detail'], 'Received document does not contain primary data')

    def testPostResponseNeedResponsesType(self):
        self.client.force_authenticate(user=self.participant)
        self.data['data']['type'] = "bad"
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_409_CONFLICT)

    def testPostResponseNeedChildRelationship(self):
        self.client.force_authenticate(user=self.participant)
        self.data['data']['relationships'] =  {
            "study": {
               "data": {
                 "type": "studies",
                 "id": str(self.study.uuid)
               }
             }
         }
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(api_response.data['child'][0], 'This field is required.')

    def testPostResponseNeedStudyRelationship(self):
        self.client.force_authenticate(user=self.participant)
        self.data['data']['relationships'] =  {
            "child": {
              "data": {
                "type": "children",
                "id": str(self.child.uuid)
              }
            }
         }
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(api_response.data['study'][0], 'This field is required.')

    def testPostResponseWithEmptyAttributes(self):
        self.client.force_authenticate(user=self.participant)
        self.data['data']['attributes'] = {}
        api_response = self.client.post(self.url, json.dumps(self.data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_201_CREATED)

    # PATCH responses
    def testPatchResponseAttributes(self):
        self.client.force_authenticate(user=self.participant)
        api_response = self.client.patch(self.response_detail_url, json.dumps(self.patch_data), content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(api_response.data['sequence'], ['first_frame', 'second_frame'])

    # Delete responses
    def testDeleteResponse(self):
        self.client.force_authenticate(user=self.participant)
        api_response = self.client.delete(self.response_detail_url, content_type="application/vnd.api+json")
        self.assertEqual(api_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
