export type PostStatus = 'pending' | 'approved' | 'rejected' | 'scheduled'
export type CalendarStatus = 'generating' | 'ready' | 'error'

export interface Post {
  id: string
  calendar_id: string
  day: number
  platform: string
  caption: string | null
  image_prompt: string | null
  image_url: string | null
  status: PostStatus
  created_at: string | null
}

export interface Calendar {
  id: string
  brand_name: string
  brand_description: string
  industry: string | null
  tone: string | null
  platforms: string | null
  num_days: number
  status: CalendarStatus
  created_at: string | null
  posts: Post[]
}

export interface BrandInput {
  brand_name: string
  brand_description: string
  industry: string
  tone: string
  platforms: string[]
  num_days: number
}
