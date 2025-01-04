// Leetspeak character substitution map
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

// Generate leetspeak variations for a given word
function generateLeetspeakVariations(word) {
    const variations = new Set([word]);
    word = word.toLowerCase();
    const indices = [...word].map((char, index) => leetSubstitutions[char] ? index : -1).filter(index => index !== -1);

    for (let length = 1; length <= indices.length; length++) {
        for (const subset of combinations(indices, length)) {
            for (const replacements of cartesianProduct(subset.map(index => leetSubstitutions[word[index]]))) {
                const wordList = [...word];
                for (let i = 0; i < subset.length; i++) {
                    wordList[subset[i]] = replacements[i];
                }
                variations.add(wordList.join(''));
            }
        }
    }
    return Array.from(variations);
}

// Generate common passwords based on keyword
function generateCommonPasswords(keyword) {
    const commonPatterns = ['123', '2023', 'password', 'admin', 'user', 'secure', 'qwerty', 'letmein', 'welcome', 'trustno1', 'master'];
    const variations = [keyword, keyword.toLowerCase(), keyword.toUpperCase(), keyword.charAt(0).toUpperCase() + keyword.slice(1)];
    const commonPasswords = new Set();
    
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

// Helper function to generate combinations of indices
function combinations(arr, length) {
    if (length === 0) return [[]];
    if (arr.length === 0) return [];
    const first = arr[0];
    const rest = arr.slice(1);
    const withFirst = combinations(rest, length - 1).map(comb => [first, ...comb]);
    const withoutFirst = combinations(rest, length);
    return withFirst.concat(withoutFirst);
}

// Helper function to generate the cartesian product of arrays
function cartesianProduct(arrays) {
    return arrays.reduce((acc, curr) => {
        const result = [];
        acc.forEach(a => {
            curr.forEach(b => {
                result.push([...a, b]);
            });
        });
        return result;
    }, [[]]);
}

// Add advanced patterns to passwords
function addAdvancedPatterns(passwords) {
    const patterns = ['123', '!', '@', '#', 'secure', '2023', 'admin'];
    const result = [];

    passwords.forEach(password => {
        patterns.forEach(pattern => {
            result.push(`${password}${pattern}`);
            result.push(`${pattern}${password}`);
            result.push(`${password}_${pattern}`);
            result.push(`${password}#${pattern}`);
        });
    });

    return passwords.concat(result);
}

// Main function to generate passwords based on keyword
function generatePasswords(keyword) {
    const commonPasswords = generateCommonPasswords(keyword);
    const leetspeakVariations = generateLeetspeakVariations(keyword);
    const patternsAddedPasswords = addAdvancedPatterns([...commonPasswords, ...leetspeakVariations]);
    return patternsAddedPasswords;
}

// Function to handle password download
function downloadPasswords(passwords) {
    const blob = new Blob([passwords.join('\n')], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'generated_passwords.txt';
    link.click();
}

// Expose the functions for use in HTML
window.generatePasswords = function(keyword) {
    return generatePasswords(keyword);
};

window.downloadPasswords = function(passwords) {
    downloadPasswords(passwords);
};
