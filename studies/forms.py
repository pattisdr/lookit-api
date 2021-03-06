import json

from django import forms
from django.forms import ModelForm, Textarea

from ace_overlay.widgets import AceOverlayWidget
from studies.models import Response, Study


class ResponseForm(forms.ModelForm):
    results = forms.CharField(widget=AceOverlayWidget(mode='json', wordwrap=True, theme='textmate', width='100%', height='100%', showprintmargin=False), required=False)
    class Meta:
        fields = (
            'study',
            'child',
            'demographic_snapshot',
            'results'
        )
        model = Response


class StudyCleanForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        min_age_months = self.cleaned_data.get('min_age_months')
        min_age_years = self.cleaned_data.get('min_age_years')
        max_age_months = self.cleaned_data.get('max_age_months')
        max_age_years = self.cleaned_data.get('max_age_years')
        if (min_age_years + min_age_months/12) > (max_age_years + max_age_months/12):
            raise forms.ValidationError('The maximum age must be greater than the minimum age.')
        return cleaned_data


class StudyEditForm(StudyCleanForm):

    class Meta:
        model = Study
        fields = ['name', 'image', 'short_description', 'long_description', 'exit_url', 'criteria', 'min_age_months', 'min_age_years', 'max_age_months', 'max_age_years', 'duration', 'contact_info', 'public']
        labels = {
            'short_description': 'Short Description',
            'long_description': 'Purpose',
            'exit_url': 'Exit URL',
            'criteria': 'Participant Eligibility',
            'contact_info': 'Researcher/Contact Information',
            'public': 'Discoverable - Do you want this study to be publicly discoverable on Lookit once activated?'
        }
        widgets = {
            'short_description': Textarea(attrs={'rows': 2}),
            'long_description': Textarea(attrs={'rows': 2}),
            'exit_url': Textarea(attrs={'rows': 1}),
            'criteria': Textarea(attrs={'rows': 1}),
            'duration': Textarea(attrs={'rows': 1}),
            'contact_info': Textarea(attrs={'rows': 1}),
        }

        help_texts = {
            'image': 'Please keep your file size less than 1 MB',
            'exit_url': "Specify the page where you want to send your participants after they've completed the study.",
            'short_description': 'Give your study a description here.',
            'long_description': 'Explain the purpose of your study here.',
        }

class StudyForm(StudyCleanForm):
    structure = forms.CharField(label='Build Study - Add JSON', widget=AceOverlayWidget(mode='json', wordwrap=True, theme='textmate', width='100%', height='100%', showprintmargin=False), required=False, help_text='Add the frames of your study as well as the sequence of those frames.  This can be added later.')

    def clean_structure(self):
         structure = self.cleaned_data['structure']
         try:
             json_data = json.loads(structure) #loads string as json
         except:
             raise forms.ValidationError("Invalid JSON")
         return json_data

    class Meta:
        model = Study
        fields = ['name', 'image', 'short_description', 'long_description', 'exit_url', 'criteria', 'min_age_years', 'min_age_months', 'max_age_years', 'max_age_months', 'duration', 'contact_info', 'public', 'structure', 'study_type']
        labels = {
            'short_description': 'Short Description',
            'long_description': 'Purpose',
            'exit_url': 'Exit URL',
            'criteria': 'Participant Eligibility',
            'contact_info': 'Researcher/Contact Information',
            'public': 'Discoverable - Do you want this study to be publicly discoverable on Lookit once activated?',
            'study_type': 'Study Type'
        }
        widgets = {
            'short_description': Textarea(attrs={'rows': 2}),
            'long_description': Textarea(attrs={'rows': 2}),
            'exit_url': Textarea(attrs={'rows': 1}),
            'criteria': Textarea(attrs={'rows': 1}),
            'duration': Textarea(attrs={'rows': 1}),
            'contact_info': Textarea(attrs={'rows': 1}),
        }
        help_texts = {
            'image': 'Please keep your file size less than 1 MB',
            'exit_url': "Specify the page where you want to send your participants after they've completed the study.",
            'short_description': 'Give your study a description here.',
            'long_description': 'Explain the purpose of your study here.',
            'study_type': "Specify the build process as well as the parameters needed by the experiment builder. If you don't know what this is, just select the default.",
        }


class StudyBuildForm(forms.ModelForm):
    structure = forms.CharField(label='Build Study - Add JSON', widget=AceOverlayWidget(mode='json', wordwrap=True, theme='textmate', width='100%', height='100%', showprintmargin=False), required=False, help_text='Add the frames of your study as well as the sequence of those frames.')

    def clean_structure(self):
         structure = self.cleaned_data['structure']
         try:
             json_data = json.loads(structure) #loads string as json
         except:
             raise forms.ValidationError("Invalid JSON")
         return json_data

    class Meta:
        model = Study
        fields = ['structure']
