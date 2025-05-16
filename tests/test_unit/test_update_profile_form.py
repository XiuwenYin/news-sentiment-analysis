from app import create_app
from app.forms import FilterForm
from werkzeug.datastructures import MultiDict

app = create_app()

def test_filter_form_valid_input():
    with app.test_request_context():
        form_data = MultiDict({
            "age": "25",
            "gender": "Male",
            "filter_by": "gender"
        })
        form = FilterForm(formdata=form_data, meta={'csrf': False})
        print(form.errors)
        assert form.validate()


def test_filter_form_missing_age():
    with app.test_request_context():
        form_data = MultiDict({
            "age": "",
            "gender": "Female",
            "filter_by": "age"
        })
        form = FilterForm(formdata=form_data)
        assert form.validate() is False
        assert "This field is required." in form.age.errors

def test_filter_form_invalid_gender_choice():
    with app.test_request_context():
        form_data = MultiDict({
            "age": "30",
            "gender": "InvalidGender",
            "filter_by": "gender"
        })
        form = FilterForm(formdata=form_data)
        assert form.validate() is False
        assert "Not a valid choice" in form.gender.errors[0]

def test_filter_form_blank_filter_by():
    with app.test_request_context():
        form_data = MultiDict({
            "age": "28",
            "gender": "Other",
            "filter_by": ""
        })
        form = FilterForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is True  