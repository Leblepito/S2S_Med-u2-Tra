export function LoadingSkeleton() {
  return (
    <div className="max-w-2xl mx-auto py-6 px-4 flex flex-col gap-4 animate-pulse" data-testid="loading-skeleton">
      {/* Language selector skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-3" />
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          ))}
        </div>
      </div>

      {/* Audio capture skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 flex flex-col items-center gap-4">
        <div className="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded-full" />
        <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full" />
      </div>

      {/* Output skeleton */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 min-h-48">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-4" />
        <div className="space-y-3">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
        </div>
      </div>
    </div>
  )
}
