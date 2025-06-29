import { getCloudRunAuthHeaders } from './cloud-run-auth';

// Server-side action result type
export type ActionResult<T = unknown> = {
  success: boolean;
  data?: T;
  error?: string;
};

// Utility function for consistent error handling across actions
const handleActionError = <T = unknown>(error: unknown, context: string): ActionResult<T> => {
  const errorMessage = error instanceof Error ? error.message : `Unknown error in ${context}`;
  console.error(`Error in ${context}:`, error);
  return { success: false, error: errorMessage };
};

// Utility function for successful action results
const createSuccessResult = <T>(data: T): ActionResult<T> => ({
  success: true,
  data,
});

export async function publishEventAction(
  eventName: string,
  payload: unknown,
  options: { timeout?: number; baseUrl?: string } = {}
): Promise<ActionResult> {
  const { timeout = 5000, baseUrl = process.env.CLOUD_RUNNER_AGENT_API_URL } = options;
  if (!baseUrl) {
    throw new Error('Base URL for Cloud Run API is not configured');
  }
  try {
    // Input validation
    if (!eventName || typeof eventName !== 'string') {
      throw new Error('Event name must be a non-empty string');
    }
    
    if (eventName.length > 100) {
      throw new Error('Event name must not exceed 100 characters');
    }

    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const publishEventUrl = `${baseUrl}/publish-event`;
    const authHeaders = await getCloudRunAuthHeaders(publishEventUrl);

    const response = await fetch(publishEventUrl, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({ event_name: eventName, payload }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    console.log(`Publishing event ${eventName} with status:`, response.status);
    
    if (!response.ok) {
      let errorMessage = 'Failed to publish event';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // If we can't parse the error response, use the default message
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`Successfully published event ${eventName}`);
    return createSuccessResult(result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return handleActionError(new Error(`Request timeout after ${timeout}ms`), `publishEventAction(${eventName})`);
    }
    return handleActionError(error, `publishEventAction(${eventName})`);
  }
}

export async function publishQueryAction(
  query: string,
  userId: string,
  sessionId?: string,
  options: { timeout?: number; baseUrl?: string } = {}
): Promise<ActionResult> {
  const { timeout = 1000000, baseUrl = process.env.CLOUD_RUNNER_AGENT_API_URL } = options;
  if (!baseUrl) {
    throw new Error('Base URL for Cloud Run API is not configured');
  }

  try {
    // Input validation
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string');
    }
    
    if (!userId || typeof userId !== 'string') {
      throw new Error('User ID must be a non-empty string');
    }
    
    if (query.length > 10000) {
      throw new Error('Query must not exceed 10,000 characters');
    }

    if (sessionId && typeof sessionId !== 'string') {
      throw new Error('Session ID must be a string if provided');
    }

    // Create AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const orchestratorUrl = `${baseUrl}/orchestrator`;
    const authHeaders = await getCloudRunAuthHeaders(orchestratorUrl);

    const response = await fetch(orchestratorUrl, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({
        query: query.trim(),
        user_id: userId,
        session_id: sessionId,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = 'Failed to publish query';
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        // If we can't parse the error response, use the default message
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return createSuccessResult(result);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return handleActionError(new Error(`Request timeout after ${timeout}ms`), 'publishQueryAction');
    }
    return handleActionError(error, 'publishQueryAction');
  }
}