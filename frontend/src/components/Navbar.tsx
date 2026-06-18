"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { BarChart3, LogOut, User, Search } from "lucide-react";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 text-brand-700 font-bold text-xl">
              <BarChart3 className="w-6 h-6" />
              StatusQuo
            </Link>
            <div className="hidden sm:flex items-center gap-6">
              <Link href="/" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                Search
              </Link>
              <Link href="/reports" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                Reports
              </Link>
              {user && (
                <Link href={`/users/${user.username}`} className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                  My Status
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <Link href="/settings" className="text-gray-600 hover:text-gray-900 text-sm">
                  <User className="w-5 h-5" />
                </Link>
                <button onClick={logout} className="text-gray-500 hover:text-gray-700" title="Logout">
                  <LogOut className="w-5 h-5" />
                </button>
                <span className="text-sm text-gray-600">{user.display_name}</span>
              </>
            ) : (
              <Link href="/login" className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700 transition">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
