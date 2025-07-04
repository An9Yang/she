export default function PersonaCardSkeleton() {
  return (
    <div className="card-modern p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            {/* Avatar skeleton */}
            <div className="w-12 h-12 rounded-full skeleton" />
            
            <div>
              <div className="h-6 w-32 skeleton mb-2 rounded" />
              <div className="h-5 w-20 skeleton rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats skeleton */}
      <div className="space-y-3">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-lg skeleton mr-3" />
          <div className="h-4 w-24 skeleton rounded" />
        </div>
        
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-lg skeleton mr-3" />
          <div className="h-4 w-36 skeleton rounded" />
        </div>
        
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-lg skeleton mr-3" />
          <div className="h-4 w-48 skeleton rounded" />
        </div>
      </div>

      {/* Button skeleton */}
      <div className="mt-5 w-full h-12 skeleton rounded-lg" />
    </div>
  )
}