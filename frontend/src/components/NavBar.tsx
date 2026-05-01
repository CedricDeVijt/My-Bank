import { NavLink } from "react-router-dom";

export function NavBar() {
  return (
    <nav>
      <div className="bg-gray-800 text-white  p-4">
        <div className="flex items-center space-x-8">
          <NavLink to={"/"}>Home</NavLink>
          <NavLink to={"Login"}>Login</NavLink>
        </div>
      </div>
    </nav>
  );
}
