import cv2
import pytesseract
def extract_number_from_image(image_path):
    """
    Load the image, preprocess it, and extract the number.
    
    Parameters:
    - image_path: Path to the image file
    
    Returns:
    - Extracted number as a string
    """
    
    # Load the image
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use adaptive thresholding to binarize the image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Invert the image for OCR
    inverted = cv2.bitwise_not(binary)
    
    # Extract text from the image
    text = pytesseract.image_to_string(inverted, config='--psm 6')
    
    # Clean the extracted text and keep only digits
    digits = ''.join(filter(str.isdigit, text))
    
    # To improve accuracy, we can keep only the largest detected number (assuming the desired number is the largest)
    if digits:
        largest_digit = max(digits, key=lambda x: digits.count(x))
        return largest_digit
    else:
        return None

# Test the function on the provided image
extracted_number = extract_number_from_image('Image.png')
print(extracted_number)