import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 获取token - 注意：这里应该从localStorage获取，但middleware无法访问localStorage
  // 所以实际的认证检查需要在客户端组件中进行
  const authCookie = request.cookies.get('auth-token')?.value
  
  // 需要保护的路由
  const protectedPaths = ['/personas', '/chat']
  const isProtectedPath = protectedPaths.some(path => 
    request.nextUrl.pathname.startsWith(path)
  )

  // 如果是受保护的路由且没有token，重定向到登录页
  if (isProtectedPath && !authCookie) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  // 如果已登录且访问auth页面，重定向到personas
  if (authCookie && request.nextUrl.pathname.startsWith('/auth')) {
    return NextResponse.redirect(new URL('/personas', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/personas/:path*', '/chat/:path*', '/auth/:path*']
}