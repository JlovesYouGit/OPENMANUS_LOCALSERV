// Test script for OpenManus login functionality
// This script tests the login validation logic

function testUsernameValidation() {
    const validateUsername = (username) => {
        // Basic validation
        if (!username.trim()) {
            return 'Please enter a username';
        }

        // Validate username format (2-20 characters, letters, numbers, underscores, hyphens)
        const usernameRegex = /^[a-zA-Z0-9_-]{2,20}$/;
        if (!usernameRegex.test(username)) {
            return 'Username must be 2-20 characters and contain only letters, numbers, underscores, and hyphens';
        }

        return null; // No error
    };

    // Test cases
    const testCases = [
        { input: '', expected: 'Please enter a username' },
        { input: 'a', expected: 'Username must be 2-20 characters and contain only letters, numbers, underscores, and hyphens' },
        { input: 'ab', expected: null },
        { input: 'user_name', expected: null },
        { input: 'user-name', expected: null },
        { input: 'username123', expected: null },
        { input: 'a'.repeat(21), expected: 'Username must be 2-20 characters and contain only letters, numbers, underscores, and hyphens' },
        { input: 'user@name', expected: 'Username must be 2-20 characters and contain only letters, numbers, underscores, and hyphens' },
        { input: 'user name', expected: 'Username must be 2-20 characters and contain only letters, numbers, underscores, and hyphens' }
    ];

    console.log('Testing username validation...');
    let passed = 0;
    let failed = 0;

    testCases.forEach((testCase, index) => {
        const result = validateUsername(testCase.input);
        const errorMessage = result || 'No error';
        const expectedMessage = testCase.expected || 'No error';
        
        if (errorMessage === expectedMessage) {
            console.log(`✓ Test ${index + 1}: PASSED`);
            passed++;
        } else {
            console.log(`✗ Test ${index + 1}: FAILED`);
            console.log(`  Input: "${testCase.input}"`);
            console.log(`  Expected: "${expectedMessage}"`);
            console.log(`  Got: "${errorMessage}"`);
            failed++;
        }
    });

    console.log(`\nResults: ${passed} passed, ${failed} failed`);
    
    if (failed === 0) {
        console.log('All tests passed! ✅');
    } else {
        console.log('Some tests failed! ❌');
    }
}

// Run the tests
testUsernameValidation();