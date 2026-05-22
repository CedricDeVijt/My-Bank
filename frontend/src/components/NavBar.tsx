import { useEffect, useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import {
  AUTH_CHANGED_EVENT,
  ApiError,
  clearTokens,
  getCurrentUser,
  loadTokens,
} from "../services/auth";
import type { UserResponse } from "../types";

export function NavBar() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isMounted = true;

    const syncCurrentUser = async () => {
      const tokens = loadTokens();

      if (!tokens?.access_token) {
        if (isMounted) {
          setCurrentUser(null);
          setCheckingSession(false);
        }
        return;
      }

      try {
        const user = await getCurrentUser();
        if (isMounted) {
          setCurrentUser(user);
        }
      } catch (caughtError: unknown) {
        if (caughtError instanceof ApiError && caughtError.status === 401) {
          clearTokens();
        }

        if (isMounted) {
          setCurrentUser(null);
        }
      } finally {
        if (isMounted) {
          setCheckingSession(false);
        }
      }
    };

    const handleAuthChange = () => {
      setCheckingSession(true);
      void syncCurrentUser();
    };

    void syncCurrentUser();
    window.addEventListener(AUTH_CHANGED_EVENT, handleAuthChange);
    window.addEventListener("storage", handleAuthChange);

    return () => {
      isMounted = false;
      window.removeEventListener(AUTH_CHANGED_EVENT, handleAuthChange);
      window.removeEventListener("storage", handleAuthChange);
    };
  }, []);

  useEffect(() => {
    if (!menuOpen) {
      return;
    }

    const handleDocumentInteraction = (event: MouseEvent | KeyboardEvent) => {
      if (event instanceof KeyboardEvent && event.key === "Escape") {
        setMenuOpen(false);
        return;
      }

      if (
        event instanceof MouseEvent &&
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleDocumentInteraction);
    document.addEventListener("keydown", handleDocumentInteraction);

    return () => {
      document.removeEventListener("mousedown", handleDocumentInteraction);
      document.removeEventListener("keydown", handleDocumentInteraction);
    };
  }, [menuOpen]);

  const handleLogout = () => {
    clearTokens();
    setCurrentUser(null);
    setMenuOpen(false);
    navigate("/");
  };

  const profileLabel = currentUser
    ? `${currentUser.first_name} ${currentUser.last_name}`
    : checkingSession && loadTokens()
      ? "Loading..."
      : "Login";

  const profileLink = currentUser ? "/dashboard" : "/login";

  return (
    <nav className="relative z-50 border-b border-white/6 bg-slate-950/90 shadow-2xl shadow-slate-950/20 backdrop-blur text-white">
      {/* Main nav container: match AuthPanel/HomePage panel look */}
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-8">
        <NavLink
          to={currentUser ? "/dashboard" : "/"}
          className="text-2xl font-semibold tracking-wide text-white transition hover:text-amber-200"
        >
          My Bank
        </NavLink>

        {currentUser ? (
          <div className="relative" ref={menuRef}>
            <button
              type="button"
              aria-haspopup="menu"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((current) => !current)}
              className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/10 hover:text-white"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-300 text-sm font-semibold text-slate-950">
                {currentUser.first_name.slice(0, 1)}
                {currentUser.last_name.slice(0, 1)}
              </span>
              <span className="max-w-40 truncate">{profileLabel}</span>
              <span
                className={`text-xs text-slate-400 transition ${menuOpen ? "rotate-180" : ""}`}
              >
                ▾
              </span>
            </button>

            {menuOpen ? (
              <div className="absolute right-0 mt-3 w-56 overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70 p-3 shadow-2xl shadow-slate-950/30 backdrop-blur z-50">
                <div className="px-3 py-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                  signed in as
                </div>
                <div className="px-3 pb-3 text-sm font-medium text-white">
                  {profileLabel}
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full items-center rounded-xl px-3 py-2 text-left text-sm text-slate-200 transition hover:bg-white/5 hover:text-white"
                >
                  Log out
                </button>
              </div>
            ) : null}
          </div>
        ) : checkingSession && loadTokens() ? (
          <span className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">
            Loading...
          </span>
        ) : (
          <NavLink
            to={profileLink}
            className={({ isActive }) =>
              `rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                isActive
                  ? "bg-amber-300 text-slate-950"
                  : "text-slate-200 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            Login
          </NavLink>
        )}
      </div>
    </nav>
  );
}
