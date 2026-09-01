# AI Prompt Engineering Log

## Prompt Category: View & UI Debugging
* **Context:** Receipt uploaded files were not persisting on submit.
* **Prompt Used:** *"i am getting reciept adding option and also limit one but after adding reciept ,niether it is showing to employee nor to the approver"*
* **Outcome:** Identified missing `enctype="multipart/form-data"` and `{{ form.receipt }}` field rendering inside `report_detail.html`.