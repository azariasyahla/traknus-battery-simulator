import { useMemo, useState } from "react";
import Navbar from "./components/Navbar";
import Banner from "./components/Banner";
import { Box, Container } from "@mui/material";
import Home from "./app/Home";

export type AppLanguage = "en" | "id";

export default function Entry() {
    const [language, setLanguage] = useState<AppLanguage>(() => {
        const saved = localStorage.getItem("traknus-lang");
        return saved === "id" ? "id" : "en";
    });

    const pageCopy = useMemo(
        () => ({
            en: {
                title: "Battery Runtime Simulator",
                subtitle:
                    "Estimate battery runtime for your selected forklift and work schedule.",
            },
            id: {
                title: "Simulator Daya Tahan Baterai",
                subtitle:
                    "Perkirakan daya tahan baterai untuk forklift dan jadwal kerja pilihan Anda.",
            },
        }),
        [],
    );

    const setAppLanguage = (lang: AppLanguage) => {
        setLanguage(lang);
        localStorage.setItem("traknus-lang", lang);
    };

    return (
        <Box sx={{ pb: 6 }}>
            <Navbar language={language} onLanguageChange={setAppLanguage} />
            <Container maxWidth="lg" sx={{ mt: 3 }}>
                <Banner
                    title={pageCopy[language].title}
                    subtitle={pageCopy[language].subtitle}
                    language={language}
                />
                <Home language={language} />
            </Container>
        </Box>
    );
}
