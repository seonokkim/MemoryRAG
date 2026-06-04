import { Outlet, NavLink, useLocation } from "react-router";
import { Home, Video, MessageCircle, User, Dumbbell } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home },
  { to: "/upload", label: "Analysis", icon: Video },
  { to: "/coach", label: "AI Coach", icon: MessageCircle },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/routine", label: "Routine", icon: Dumbbell },
];

export function Layout() {
  const location = useLocation();
  const hideNav = ["/analysis", "/report", "/dev"].some(p =>
    location.pathname.startsWith(p)
  );

  return (
    <div className="min-h-screen bg-[#FAFAFA] flex justify-center">
      <div className="w-full max-w-[430px] min-h-screen bg-white flex flex-col relative shadow-sm">
        <main className="flex-1 overflow-y-auto" style={{ paddingBottom: hideNav ? 0 : 80 }}>
          <Outlet />
        </main>

        {!hideNav && (
          <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[430px] bg-white border-t border-[#E4E4E7] z-50">
            <div className="flex items-center justify-around h-[68px] px-2">
              {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
                const isActive =
                  to === "/"
                    ? location.pathname === "/"
                    : location.pathname.startsWith(to);
                return (
                  <NavLink
                    key={to}
                    to={to}
                    className="flex flex-col items-center gap-0.5 py-2 px-3 min-w-0"
                  >
                    <Icon
                      size={22}
                      strokeWidth={isActive ? 2.2 : 1.8}
                      color={isActive ? "#09090B" : "#A1A1AA"}
                    />
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? "#09090B" : "#A1A1AA",
                        lineHeight: "1.2",
                      }}
                    >
                      {label}
                    </span>
                  </NavLink>
                );
              })}
            </div>
          </nav>
        )}
      </div>
    </div>
  );
}
