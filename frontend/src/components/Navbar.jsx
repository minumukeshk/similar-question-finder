import { Link, useNavigate } from "react-router-dom";
import { BookOpen, Clock, LogOut } from "lucide-react";

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="sticky top-0 z-50 bg-card border-b border-border">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2 font-bold text-white text-base tracking-tight"
        >
          <BookOpen size={20} className="text-accent" />
          <span>
            Similar<span className="text-accent">Q</span>
          </span>
        </Link>

        {/* Right-side nav */}
        <div className="flex items-center gap-1">
          <Link
            to="/history"
            className="btn-ghost flex items-center gap-1.5"
          >
            <Clock size={15} />
            History
          </Link>

          <button
            onClick={handleLogout}
            className="btn-ghost flex items-center gap-1.5 text-red-400 hover:text-red-300"
          >
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
