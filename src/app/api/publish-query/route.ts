import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { publishQueryAction } from '@/lib/server-actions';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { query, sessionId } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json({ 
        error: 'Query is required and must be a string' 
      }, { status: 400 });
    }

    // Use the authenticated user's ID
    const userId = session.user.id;

    // Call the server-side action with authentication
    const result = await publishQueryAction(query, userId, sessionId);

    if (result.success) {
      return NextResponse.json({
        success: true,
        data: result.data,
        message: 'Query published successfully'
      });
    } else {
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to publish query'
      }, { status: 500 });
    }

  } catch (error) {
    console.error('Error in publish-query API:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}