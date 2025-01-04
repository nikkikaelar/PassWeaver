# Ultimate Password List Generator for Brute Force Attacks

## Description
Welcome to the **Password Generator!**  
This tool generates complex password variations by combining leetspeak, common patterns, and machine learning techniques. Ideal for penetration testers, cybersecurity enthusiasts, and researchers, it helps in generating high-quality password lists for brute-force testing.

**Features:**
- Leetspeak password variations.
- Common password patterns and combinations.
- Machine learning to generate more sophisticated variations.
- Stylish terminal UI with hacker-like visuals.
- Passwords saved to a text file for use in security testing.

## Requirements
To run this script, you will need:
- Python 3.x
- Libraries: `itertools`, `random`, `string`, `re`, `termcolor`, `time`, `sys`, `joblib`, `sklearn`
- You can install the required libraries by running:
  ```
  pip install termcolor joblib scikit-learn
  ```

## Usage

1. Clone the repository or download the script.
2. Ensure you have the necessary Python libraries installed.
3. Run the script in your terminal:

   ```
   python password_generator.py
   ```

4. Enter a keyword when prompted to generate passwords.
   - The script will generate variations of your keyword with common patterns and leetspeak.
   - Passwords will be enhanced using machine learning based on a corpus of common passwords.
   
5. The generated passwords will be displayed in the terminal and saved to a file `generated_passwords.txt`.

## Script Breakdown

### 1. **Leetspeak Generation:**
   - The script generates variations of a word using leetspeak, including substitutions like `a` → `@`, `e` → `3`, and others.

### 2. **Common Password Patterns:**
   - The generator creates password variations by adding common patterns (e.g., `123`, `secure`, `admin`) to the input keyword.

### 3. **Machine Learning:**
   - It uses a `LogisticRegression` model trained on a list of common passwords to create more sophisticated variations.

### 4. **Progress Bar:**
   - A stylish progress bar is displayed to visualize the generation process, enhancing the user experience.

### 5. **Hacker-Style UI:**
   - The terminal UI is designed with a hacker-inspired theme, using color and delay to simulate a “real” hacking experience.

### 6. **Password File Output:**
   - After the passwords are generated, they are saved to `generated_passwords.txt` for further use.

## Example

```
Enter a keyword to generate passwords: 
=> password

Generated Passwords:
password123
password2023
password!secure
...
```

## Warning 
This tool is provided for educational and research purposes only. Use it responsibly and only in environments where you have permission to perform security testing.

---

