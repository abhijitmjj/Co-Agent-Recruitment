import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/lib/auth'
import { adminAuth } from '@/lib/firebase-admin'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session || !session.user?.id) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
  }
  try {
    const customToken = await adminAuth.createCustomToken(session.user.id)
    return NextResponse.json({ customToken })
  } catch (error) {
    console.error('[Auth Firebase] Error creating custom token:', error)
    return NextResponse.json({ error: 'Failed to create custom token' }, { status: 500 })
  }
}