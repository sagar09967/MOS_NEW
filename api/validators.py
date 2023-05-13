import os

import pandas as pd
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class AllowedExtensionsValidator:
    def __init__(self, allowed_extensions):
        self.allowed_extensions = allowed_extensions

    def __call__(self, value):
        ext = os.path.splitext(value.name)[1]  # Extract the file extension
        if not ext.lower() in self.allowed_extensions:
            raise ValidationError(
                f"Only the following file extensions are allowed: {', '.join(self.allowed_extensions)}")


class ExcelFileValidator:
    def __init__(self, columns):
        self.columns = columns

    def __call__(self, value):
        # Read the Excel file into a DataFrame
        try:
            df = pd.read_excel(value, header=None)
        except Exception as e:
            raise ValidationError(f"Error reading the Excel file: {str(e)}")

        # Check if all the required columns are present
        missing_columns = set(self.columns) - set(df.iloc[0])
        if missing_columns:
            raise ValidationError(f"The following columns are missing in the Excel file: {', '.join(missing_columns)}")