import { createRoot } from "react-dom/client";
import { StrictMode } from "react";
import Entry from "./Entry";
import { Theme } from "./theme";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <Theme>
            <Entry />
        </Theme>
    </StrictMode>,
);
