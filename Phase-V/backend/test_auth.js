#!/usr/bin/env node
// Test script to verify authentication and task functionality

const BASE_URL = 'http://127.0.0.1:8000';

async function testAuthFlow() {
  console.log('Testing authentication flow...\n');

  // Test 1: Try to access protected endpoint without authentication
  console.log('1. Testing protected endpoint without authentication...');
  try {
    const response = await fetch(`${BASE_URL}/api/tasks/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    console.log(`   Response: ${response.status} ${response.statusText}`);
    if (response.status === 401) {
      console.log('   ✅ Correctly returns 401 without authentication');
    } else {
      console.log('   ❌ Expected 401, got different response');
    }
  } catch (error) {
    console.error('   ❌ Error testing protected endpoint:', error.message);
  }

  // Test 2: Try to access public endpoint
  console.log('\n2. Testing public endpoint...');
  try {
    const response = await fetch(`${BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    console.log(`   Response: ${response.status} ${response.statusText}`);
    if (response.status === 200) {
      console.log('   ✅ Health endpoint working correctly');
    } else {
      console.log('   ❌ Health endpoint not working as expected');
    }
  } catch (error) {
    console.error('   ❌ Error testing health endpoint:', error.message);
  }

  // Test 3: Try to access auth endpoints
  console.log('\n3. Testing authentication endpoints...');
  try {
    const response = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'password'
      })
    });
    console.log(`   Login endpoint response: ${response.status} ${response.statusText}`);

    // Test signup endpoint too
    const signupResponse = await fetch(`${BASE_URL}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      })
    });
    console.log(`   Signup endpoint response: ${signupResponse.status} ${signupResponse.statusText}`);
  } catch (error) {
    console.error('   ❌ Error testing auth endpoints:', error.message);
  }

  console.log('\nTest completed. Backend authentication system is accessible.');
}

// Run the test
testAuthFlow().catch(console.error);