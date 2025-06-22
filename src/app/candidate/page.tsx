import dynamic from 'next/dynamic';

// Load the client-side CandidateForm without server-side rendering
const CandidateForm = dynamic(
  () => import('@/components/candidate-form'),
  { ssr: false }
);

export default function CandidatePage() {
  return <CandidateForm />;
}