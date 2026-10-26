import Home from "@/app/Home";
import {
    createContext,
    useContext,
    useState,
    ReactNode,
    useEffect,
} from "react";

type LocationId = "home";
interface NavigatorState {
    location: LocationId;
    setLocation: (location: LocationId) => void;
}

const NavigatorContext = createContext<NavigatorState | undefined>(undefined);

type NavigatorProps = {
    children?: ReactNode;
};

export const NavigatorProvider = ({ children }: NavigatorProps) => {
    const [location, setLocation] = useState<LocationId>(() => {
        if (typeof window !== "undefined") {
            return (localStorage.getItem("location") || "home") as LocationId;
        }
        return "home" as LocationId;
    });

    useEffect(() => {
        localStorage.setItem("location", location);
    }, [location]);

    return (
        <NavigatorContext.Provider value={{ location, setLocation }}>
            {children}
        </NavigatorContext.Provider>
    );
};

export const useNavigator = () => {
    const context = useContext(NavigatorContext);
    if (!context)
        throw new Error("useNavigator must be used within a NavigatorProvider");
    return context;
};

export const Content = () => {
    const { location } = useNavigator();

    switch (location) {
        case "home":
            return <Home language="en" />;
        default:
            return <div>Page not found</div>;
    }
};
