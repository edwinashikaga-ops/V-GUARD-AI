import { useLanguage } from "@/contexts/LanguageContext";

export default function Portal() {
  const { t } = useLanguage();
  return <div className="p-8"><h1>{t("portal.dashboard")}</h1></div>;
}
