const leetSubstitutions = {
    'a': ['@', '4', '^'],
    'b': ['8', '6'],
    'c': ['(', '{', '[', '<'],
    'e': ['3', '&'],
    'g': ['6', '9', 'q'],
    'i': ['1', '!', '|', 'l'],
    'l': ['1', '|', '/', '\\'],
    'o': ['0', 'Q', '*'],
    's': ['$', '5', 'z'],
    't': ['7', '+', '†'],
    'z': ['2', 's']
};

const commonPatterns = ['123', '2023', 'password', 'admin', 'user', 'secure', 'qwerty', 'letmein', 'welcome', 'trustno1', 'master'];

let generatedPasswords = [];

// Generate leetspeak variations for a given word with alternating complexity
function generateLeetspeakVariations(word) {
    let variations = new Set([word]);
    word = word.toLowerCase();
    let indices = [...word].map((char, idx) => leetSubstitutions[char] ? idx : -1).filter(idx => idx !== -1);

    for (let length = 1; length <= indices.length; length++) {
        for (let subset of getCombinations(indices, length)) {
            for (let replacements of getProduct(...subset.map(idx => leetSubstitutions[word[idx]]))) {
                let wordList = [...word];
                subset.forEach((idx, i) => {
                    wordList[idx] = replacements[i];
                });
                variations.add(wordList.join(''));
            }
        }
    }
    return Array.from(variations);
}

// Generate combinations of indices
function getCombinations(arr, length) {
    let result = [];
    function combine(start, path) {
        if (path.length === length) {
            result.push(path);
            return;
        }
        for (let i = start; i < arr.length; i++) {
            combine(i + 1, [...path, arr[i]]);
        }
    }
    combine(0, []);
    return result;
}

// Get all possible combinations of elements
function getProduct(...arrays) {
    return arrays.reduce((acc, arr) => {
        let result = [];
        acc.forEach(a => arr.forEach(b => result.push([...a, b])));
        return result;
    }, [[]]);
}

// Add common patterns based on user input
function generateCommonPasswords(keyword) {
    let variations = [keyword, keyword.toLowerCase(), keyword.toUpperCase(), keyword.charAt(0).toUpperCase() + keyword.slice(1)];
    let commonPasswords = new Set();

    variations.forEach(variation => {
        commonPatterns.forEach(pattern => {
            commonPasswords.add(`${variation}${pattern}`);
            commonPasswords.add(`${pattern}${variation}`);
            commonPasswords.add(`${variation}_${pattern}`);
            commonPasswords.add(`${pattern}_${variation}`);
        });
    });
    return Array.from(commonPasswords);
}

// Generate final list of passwords
function generatePasswords(keyword) {
    let commonPasswords = generateCommonPasswords(keyword);
    let keywordVariations = generateLeetspeakVariations(keyword);
    let finalPasswords = new Set([...commonPasswords, ...keywordVariations]);
    return Array.from(finalPasswords);
}

// Handle progress bar
function updateProgressBar(progress) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${progress}%`;
}

// Function to handle password generation and progress display
function startPasswordGeneration() {
    const keyword = document.getElementById('keyword').value.trim();
    if (!/^[a-zA-Z0-9]+$/.test(keyword)) {
        alert("Please enter a valid keyword (letters and numbers only).");
        return;
    }

    // Hide the input and show the progress
    document.getElementById('keyword').disabled = true;
    document.querySelector("button").disabled = true;
    document.getElementById('password-list').innerHTML = '';
    document.getElementById('password-count').innerHTML = '';
    document.getElementById('download-btn').style.display = 'none';

    let totalSteps = 100;
    let generatedPasswords = [];
    let step = 0;

    let interval = setInterval(() => {
        step++;
        updateProgressBar((step / totalSteps) * 100);
        if (step >= totalSteps) {
            clearInterval(interval);
            generatedPasswords = generatePasswords(keyword);
            displayGeneratedPasswords(generatedPasswords);
            showDownloadButton();
        }
    }, 50);
}

// Display generated passwords
function displayGeneratedPasswords(passwords) {
    const passwordList = document.getElementById('password-list');
    passwords.forEach(password => {
        const li = document.createElement('li');
        li.textContent = password;
        passwordList.appendChild(li);
    });

    // Display total number of passwords
    const passwordCount = document.getElementById('password-count');
    passwordCount.textContent = `Total Passwords Generated: ${passwords.length}`;
}

// Show download button
function showDownloadButton() {
    document.getElementById('download-btn').style.display = 'inline-block';
}

// Download the generated passwords as a .txt file
function downloadPasswords() {
    const blob = new Blob([generatedPasswords.join('\n')], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'generated_passwords.txt';
    link.click();
}
