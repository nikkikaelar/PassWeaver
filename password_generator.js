const leetSubstitutions = {
    'a': ['@', '4', '^'],
    'b': ['8', '6'],
    'c': ['(', '{', '[', '<'],
    'e': ['3', '&'],
    'g': ['6', '9', 'q'],
    'i': ['1', '!', '|', 'l'],
    'o': ['0', 'Q', '*'],
    's': ['$', '5', 'z'],
    't': ['7', '+', '†'],
    'z': ['2', 's']
};

const commonPatterns = ['123', '2023', 'password', 'admin', 'user', 'secure', 'qwerty', 'letmein', 'welcome', 'trustno1', 'master'];

// Function to generate leetspeak variations
function generateLeetspeakVariations(word) {
    let variations = new Set([word]);
    word = word.toLowerCase();
    const indices = [...word].map((char, i) => leetSubstitutions[char] ? i : -1).filter(i => i !== -1);

    for (let length = 1; length <= indices.length; length++) {
        for (let subset of combinations(indices, length)) {
            for (let replacements of cartesianProduct(...subset.map(i => leetSubstitutions[word[i]]))) {
                let wordList = [...word];
                subset.forEach((idx, i) => wordList[idx] = replacements[i]);
                variations.add(wordList.join(''));
            }
        }
    }

    return [...variations];
}

// Function to generate common password patterns
function generateCommonPasswords(keyword) {
    let variations = [keyword, keyword.toLowerCase(), keyword.toUpperCase(), keyword.charAt(0).toUpperCase() + keyword.slice(1)];
    let commonPasswords = new Set();
    variations.forEach(variation => {
        commonPatterns.forEach(pattern => {
            commonPasswords.add(variation + pattern);
            commonPasswords.add(pattern + variation);
            commonPasswords.add(variation + '_' + pattern);
            commonPasswords.add(pattern + '_' + variation);
        });
    });
    return [...commonPasswords];
}

// Helper function for generating combinations
function combinations(arr, size) {
    const result = [];
    const combine = (start, current) => {
        if (current.length === size) {
            result.push([...current]);
            return;
        }
        for (let i = start; i < arr.length; i++) {
            current.push(arr[i]);
            combine(i + 1, current);
            current.pop();
        }
    };
    combine(0, []);
    return result;
}

// Helper function for cartesian product
function cartesianProduct(...arrays) {
    return arrays.reduce((a, b) => a.flatMap(d => b.map(e => [...d, e])), [[]]);
}

// Function to generate the final list of passwords
function generatePasswords(keyword) {
    let commonPasswords = generateCommonPasswords(keyword);
    let leetspeakVariations = generateLeetspeakVariations(keyword);
    return [...new Set([...commonPasswords, ...leetspeakVariations])];
}

// Display progress bar
function updateProgressBar(percentage) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = percentage + '%';
}

// Display passwords and update count
function displayPasswords(passwords) {
    const passwordList = document.getElementById('password-list');
    passwordList.innerHTML = '';
    passwords.forEach(password => {
        const li = document.createElement('li');
        li.textContent = password;
        passwordList.appendChild(li);
    });
    document.getElementById('password-count').textContent = `Total Passwords Generated: ${passwords.length}`;
    document.getElementById('download-btn').style.display = 'inline-block';
}

// Save passwords to a file
function downloadPasswords() {
    const passwords = document.querySelectorAll('#password-list li');
    const passwordArray = Array.from(passwords).map(li => li.textContent);
    const blob = new Blob([passwordArray.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'generated_passwords.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Start the password generation process
function startPasswordGeneration() {
    const keyword = document.getElementById('keyword').value.trim();
    if (!keyword.match(/^[a-zA-Z0-9]+$/)) {
        alert('Invalid input. Please enter a keyword with letters and numbers only.');
        return;
    }

    // Disable input while generating passwords
    document.getElementById('keyword').disabled = true;
    document.querySelector('button').disabled = true;

    let passwords = [];
    let totalSteps = 100; // Simulated progress steps
    let step = 0;

    // Simulate the password generation and progress bar update
    let interval = setInterval(() => {
        let percentage = (step / totalSteps) * 100;
        updateProgressBar(percentage);

        if (step === totalSteps) {
            clearInterval(interval);
            passwords = generatePasswords(keyword);
            displayPasswords(passwords);
            document.getElementById('keyword').disabled = false;
            document.querySelector('button').disabled = false;
        }

        step++;
    }, 50);
}
