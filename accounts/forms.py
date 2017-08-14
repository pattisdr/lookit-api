from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.forms.widgets import DateInput

from accounts.models import DemographicData, User, Child
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm
from studies.models import Study


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('password', )


class ParticipantSignupForm(UserCreationForm):

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'given_name', 'contact_name')
        exclude = ('user_permissions', 'groups', '_identicon', 'organization',
                   'is_active', 'is_staff', 'is_superuser', 'last_login',
                   'middle_name', 'last_name')
        labels = {
            'given_name': "Username"
        }


class ParticipantUpdateForm(forms.ModelForm):
    username = forms.EmailField(disabled=True, label="Email")

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            kwargs.pop('user')
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    class Meta:
        model = User
        fields = ('username', 'given_name', 'contact_name')
        labels = {
            'given_name': "Username"
        }


class ParticipantPasswordForm(PasswordChangeForm):
    class Meta:
        model = User


class EmailPreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email_next_session', 'email_new_studies', 'email_results_published', 'email_personally')
        labels = {
            'email_next_session': "It's time for another session of a study we are currently participating in",
            'email_new_studies': "A new study is available for one of my children",
            'email_results_published': "The results of a study we participated in are published",
            'email_personally': "A researcher needs to email me personally if I report a technical problem or there are questions about my responses (for example, if I reported two different birthdates for a child)."
        }


class DemographicDataForm(forms.ModelForm):
    race_identification = forms.MultipleChoiceField(
        choices = DemographicData.RACE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label="What category(ies) does your family identify as?",
        required=False
    )
    class Meta:
        model = DemographicData
        exclude = ('created_at', 'previous', 'user', 'extra', 'uuid' )
        fields = ('country', 'state', 'density', 'languages_spoken_at_home', 'number_of_children', 'child_birthdays', 'number_of_guardians',
        'number_of_guardians_explanation', 'race_identification', 'age', 'gender', 'education_level', 'spouse_education_level', 'annual_income',
        'number_of_books', 'lookit_referrer', 'additional_comments')

        help_texts = {
            'child_birthdays': 'Enter as a comma-separated list: YYYY-MM-DD, YYYY-MM-DD, ...'
        }

        labels = {
            'country': 'What country do you live in?',
            'state': 'What state do you live in?',
            'density': 'How would you describe the area where you live?',
            'languages_spoken_at_home': 'What language(s) does your family speak at home?',
            'number_of_children': 'How many children do you have?',
            'child_birthdays': 'For each child, please enter his or her birthdate:',
            'number_of_guardians': 'How many parents/guardians do your children live with?',
            'race_identification': 'What category(ies) does your family identify as?',
            'age': "What is your age?",
            'gender': "What is your gender?",
            'education_level': "What is the highest level of education you've completed?",
            'spouse_education_level': 'What is the highest level of education your spouse has completed?',
            'annual_income': 'What is your approximate family yearly income (in US dollars)?',
            'number_of_books': "About how many children's books are there in your home?",
            'additional_comments': "Anything else you'd like us to know?",
            'lookit_referrer': 'How did you hear about Lookit?',
            'number_of_guardians_explanation': 'If the answer varies due to shared custody arrangements or travel, please enter the number of parents/guardians your children are usually living with or explain.',
        }

        widgets = {
            'languages_spoken_at_home': forms.Textarea(attrs={'rows': 1}),
            'additional_comments': forms.Textarea(attrs={'rows':2}),
            'number_of_guardians_explanation': forms.Textarea(attrs={'rows':2}),
            'lookit_referrer': forms.Textarea(attrs={'rows':2})
        }


class ChildForm(forms.ModelForm):
    birthday = forms.DateField(widget=DateInput(attrs={'type': 'date'}), help_text="This lets us figure out exactly how old your child is when he or she participates in a study. We never publish children\'s birthdates or information that would allow a reader to calculate the birthdate.")

    class Meta:
        model = Child
        fields = ('given_name', 'birthday', 'gender', 'age_at_birth', 'additional_information')

        labels = {
            'given_name': 'First Name',
            'birthday': "Birthday",
            'age_at_birth': 'Gestational Age at Birth',
            'additional_information': "Any additional information you'd like us to know"
        }

        help_texts = {
            'given_name': 'This lets you select the correct child to participate in a particular study. A nickname or initials are fine! We may include your child\'s name in email to you (for instance, "There\'s a new study available for Molly!") but will never publish names or use them in our research.',
            'additional_information': "for instance, diagnosed developmental disorders or vision or hearing problems"
        }
