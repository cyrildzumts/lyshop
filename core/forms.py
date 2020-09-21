from django import forms



class ListField(forms.TypedMultipleChoiceField):

    def to_python(self, value):
        return map(self.coerce, value)

class IntergerListField(ListField):

    def __init__(self, *, coerce=int, **kwargs):
        self.coerce = int
        self.empty_value = kwargs.pop('empty_value', [])
        super().__init__(**kwargs)


    def to_python(self, value):
        return map(int, value)
    
    
    def validate(self, value):
        if not isinstance(value, int):
            raise forms.ValidationError(f"IntergerListField only accept value of type int. Received value \"{value}\"")
