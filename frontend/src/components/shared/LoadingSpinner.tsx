export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8 text-slate-400">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-500 border-t-transparent mr-2" />
      <span>Loading...</span>
    </div>
  );
}

