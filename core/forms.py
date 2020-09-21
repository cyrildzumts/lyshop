from django import forms

class ListField(forms.TypedMultipleChoiceField):

    def to_python(self, value):
        return map(self.coerce, value)
