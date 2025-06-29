// Client-side actions that call authenticated API routes

export type ActionResult<T = unknown> = {
  success: boolean;
  data?: T;
  error?: string;
};

/**
 * Client-side function to publish a query via authenticated API route
 */
export async function publishQueryAction(
  query: string,
  sessionId?: string
): Promise<ActionResult> {
  try {
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string');
    }

    const response = await fetch('/api/publish-query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        sessionId,
      }),
    });

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
    return { success: true, data: result.data };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('Error in publishQueryAction:', error);
    return { success: false, error: errorMessage };
  }
}