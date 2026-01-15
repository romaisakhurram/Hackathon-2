#!/usr/bin/env node
// Test script to verify complete authentication and task flow

const BASE_URL = 'http://127.0.0.1:8000';

async function testCompleteFlow() {
  console.log('Testing complete authentication and task flow...\n');

  // Step 1: Register a new user
  console.log('1. Registering a new user...');
  try {
    const signupResponse = await fetch(`${BASE_URL}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: 'Test User',
        email: 'testuser@example.com',
        password: 'securepassword123'
      })
    });

    const signupData = await signupResponse.json();
    console.log(`   Signup response: ${signupResponse.status} ${signupResponse.statusText}`);

    if (signupResponse.status === 200 && signupData.access_token) {
      console.log('   ✅ User registered successfully');
      const token = signupData.access_token;
      console.log('   ✅ JWT token received');

      // Step 2: Try to access tasks with the token
      console.log('\n2. Accessing tasks with authentication token...');
      try {
        const tasksResponse = await fetch(`${BASE_URL}/api/tasks/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
        console.log(`   Tasks response: ${tasksResponse.status} ${tasksResponse.statusText}`);

        if (tasksResponse.status === 200) {
          const tasksData = await tasksResponse.json();
          console.log('   ✅ Tasks endpoint accessible with valid token');
          console.log(`   ✅ Retrieved ${Array.isArray(tasksData) ? tasksData.length : 0} tasks`);
        } else if (tasksResponse.status === 404) {
          console.log('   ⚠️ Tasks endpoint may have wrong path - got 404');
        } else {
          console.log('   ❌ Unexpected response from tasks endpoint:', tasksData);
        }
      } catch (tasksError) {
        console.error('   ❌ Error accessing tasks:', tasksError.message);
      }

      // Step 3: Try to create a task with the token
      console.log('\n3. Creating a new task with authentication token...');
      try {
        const createTaskResponse = await fetch(`${BASE_URL}/api/tasks/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: 'Test Task from API',
            description: 'This is a test task created via API',
            priority: 1,
            status: 'pending'
          })
        });
        console.log(`   Create task response: ${createTaskResponse.status} ${createTaskResponse.statusText}`);

        if (createTaskResponse.status === 200) {
          const taskData = await createTaskResponse.json();
          console.log('   ✅ Task created successfully');
        } else {
          const errorData = await createTaskResponse.json().catch(() => ({}));
          console.log('   ❌ Task creation failed:', errorData);
        }
      } catch (createError) {
        console.error('   ❌ Error creating task:', createError.message);
      }
    } else {
      console.log('   ❌ User registration failed or no token returned');
      console.log('   Response data:', signupData);
    }
  } catch (error) {
    console.error('   ❌ Error during signup:', error.message);
  }

  console.log('\nComplete flow test completed.');
}

// Run the test
testCompleteFlow().catch(console.error);