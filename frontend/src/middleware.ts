import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 临时跳过认证 - 开发模式
  return NextResponse.next()
  
  // 原始认证逻辑（暂时注释）
  /*
  // 获取token
  const token = request.cookies.get('token')?.value || 
    request.headers.get('authorization')?.replace('Bearer ', '')

  // 需要保护的路由
  const protectedPaths = ['/personas', '/chat']
  const isProtectedPath = protectedPaths.some(path => 
    request.nextUrl.pathname.startsWith(path)
  )

  // 如果是受保护的路由且没有token，重定向到登录页
  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  // 如果已登录且访问auth页面，重定向到personas
  if (token && request.nextUrl.pathname.startsWith('/auth')) {
    return NextResponse.redirect(new URL('/personas', request.url))
  }

  return NextResponse.next()
  */
}

export const config = {
  matcher: ['/personas/:path*', '/chat/:path*', '/auth/:path*']
}