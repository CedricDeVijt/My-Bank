import {NavLink} from "react-router-dom";

export function NavBar() {
    return (
        <nav className="border-b border-white/6 bg-[#071827]/95 text-white backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-8">
                <NavLink
                    to="/home"
                    className="text-2xl font-semibold tracking-wide text-white"
                    style={{fontFamily: '"Times New Roman", Times, serif', letterSpacing: '0.06em'}}
                >
                    My Bank
                </NavLink>
                <NavLink
                    to="/login"
                    className={({isActive}) =>
                        isActive ? "text-amber-200" : "transition hover:text-amber-200"
                    }
                >
                    Login
                </NavLink>
            </div>
        </nav>
    );
}
