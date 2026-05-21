import app from './app';
import { Server } from 'http';

const PORT = 3050;
const BASE_URL = `http://localhost:${PORT}/api`;

function logTest(name: string, success: boolean, details?: string) {
  const symbol = success ? '✅' : '❌';
  console.log(`${symbol} ${name}`);
  if (details) console.log(`   ${details}`);
}

async function runTests() {
  console.log('\n--- STARTING AUTOMATED API VERIFICATION SUITE ---');
  let server: Server | null = null;

  try {
    // 1. Boot up testing server
    server = app.listen(PORT);
    console.log(`📡 Temporary test server running on port ${PORT}...`);

    let createdTaskId = '';

    // Test 1: Fetch initial tasks
    const getRes = await fetch(`${BASE_URL}/tasks`);
    const getBody = await getRes.json() as any;
    const t1Success = getRes.ok && getBody.success && Array.isArray(getBody.data) && getBody.data.length === 3;
    logTest('GET /api/tasks (Initial Seed Data Check)', t1Success, `Tasks Count: ${getBody.data?.length || 0}`);

    // Test 2: Create a valid task
    const postRes = await fetch(`${BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Master Advanced Agentic Coding',
        description: 'Practice building highly typed modular backend projects using deepmind antigravity.',
        priority: 'high',
      }),
    });
    const postBody = await postRes.json() as any;
    const t2Success = postRes.status === 201 && postBody.success && postBody.data.id !== undefined;
    if (t2Success) createdTaskId = postBody.data.id;
    logTest('POST /api/tasks (Create Valid Task)', t2Success, `New Task ID: ${createdTaskId}`);

    // Test 3: Attempt duplicate title validation
    const dupRes = await fetch(`${BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Master Advanced Agentic Coding',
        description: 'This is a duplicate and should fail.',
      }),
    });
    const dupBody = await dupRes.json() as any;
    const t3Success = dupRes.status === 400 && !dupBody.success;
    logTest('POST /api/tasks (Reject Duplicate Title)', t3Success, `Error Msg: "${dupBody.error}"`);

    // Test 4: Attempt invalid field validation
    const badRes = await fetch(`${BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Sh', // Too short
        description: 'Valid description',
        status: 'not-a-valid-status', // Bad status
      }),
    });
    const badBody = await badRes.json() as any;
    const t4Success = badRes.status === 400 && !badBody.success && Array.isArray(badBody.details);
    logTest('POST /api/tasks (Reject Invalid Inputs)', t4Success, `Validation Errors: ${JSON.stringify(badBody.details)}`);

    // Test 5: Fetch specific task by ID
    const getByIdRes = await fetch(`${BASE_URL}/tasks/${createdTaskId}`);
    const getByIdBody = await getByIdRes.json() as any;
    const t5Success = getByIdRes.ok && getByIdBody.success && getByIdBody.data.id === createdTaskId;
    logTest('GET /api/tasks/:id (Fetch Created Task)', t5Success, `Fetched Title: "${getByIdBody.data?.title}"`);

    // Test 6: Update specific task status
    const updateRes = await fetch(`${BASE_URL}/tasks/${createdTaskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'completed',
        priority: 'medium',
      }),
    });
    const updateBody = await updateRes.json() as any;
    const t6Success = updateRes.ok && updateBody.success && updateBody.data.status === 'completed' && updateBody.data.priority === 'medium';
    logTest('PUT /api/tasks/:id (Update Task Details)', t6Success, `Updated Status: "${updateBody.data?.status}", Priority: "${updateBody.data?.priority}"`);

    // Test 7: Delete specific task
    const delRes = await fetch(`${BASE_URL}/tasks/${createdTaskId}`, {
      method: 'DELETE',
    });
    const delBody = await delRes.json() as any;
    const t7Success = delRes.ok && delBody.success;
    logTest('DELETE /api/tasks/:id (Remove Task)', t7Success);

    // Test 8: Verify deletion clean-up
    const cleanGetRes = await fetch(`${BASE_URL}/tasks`);
    const cleanGetBody = await cleanGetRes.json() as any;
    const t8Success = cleanGetRes.ok && cleanGetBody.data.length === 3;
    logTest('GET /api/tasks (Verify Task Count is Restored)', t8Success, `Tasks Count: ${cleanGetBody.data?.length || 0}`);

    console.log('\n======================================');
    if (t1Success && t2Success && t3Success && t4Success && t5Success && t6Success && t7Success && t8Success) {
      console.log('🏆 ALL AUTOMATED TESTS PASSED SUCCESSFULLY! 🏆');
    } else {
      console.log('❌ SOME TESTS ENCOUNTERED FAILURES ❌');
    }
    console.log('======================================\n');

  } catch (error) {
    console.error('💥 Test suite execution crashed:', error);
  } finally {
    if (server) {
      server.close(() => {
        console.log('🔌 Test server shut down.');
        process.exit(0);
      });
    }
  }
}

runTests();
