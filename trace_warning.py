import warnings
import traceback

# Custom warning handler to show traceback
def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
    print(f'Warning: {message}')
    print(f'Category: {category}')
    print(f'File: {filename}:{lineno}')
    traceback.print_stack()
    print('-' * 50)

# Set the custom warning handler
warnings.showwarning = warn_with_traceback

# Import the Manus agent
from app.agent.manus import Manus

print("Import completed successfully")