import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "zh", name: "中文 (Chinese)" },
  { code: "ja", name: "日本語 (Japanese)" },
  { code: "ko", name: "한국어 (Korean)" },
  { code: "es", name: "Español (Spanish)" },
  { code: "fr", name: "Français (French)" },
  { code: "de", name: "Deutsch (German)" },
  { code: "it", name: "Italiano (Italian)" },
  { code: "pt", name: "Português (Portuguese)" },
  { code: "ru", name: "Русский (Russian)" },
  { code: "ar", name: "العربية (Arabic)" },
  { code: "hi", name: "हिन्दी (Hindi)" },
];

export const Settings = () => {
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [isLoading, setIsLoading] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  console.log("Settings component rendered");

  // Load saved language preference on component mount
  useEffect(() => {
    const loadLanguagePreference = async () => {
      try {
        const response = await fetch("/api/settings/language");
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.language) {
            setSelectedLanguage(data.language);
          }
        }
      } catch (error) {
        console.error("Error loading language preference:", error);
      }
    };

    loadLanguagePreference();
  }, []);

  const handleLanguageChange = async (value: string) => {
    setSelectedLanguage(value);
    setIsLoading(true);
    
    try {
      const response = await fetch("/api/settings/language", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ language: value }),
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success(`Language set to ${LANGUAGES.find(lang => lang.code === value)?.name || value}`);
      } else {
        throw new Error(data.error || "Failed to save language preference");
      }
    } catch (error) {
      console.error("Error saving language preference:", error);
      toast.error("Failed to save language preference");
      // Revert to previous selection on error
      const response = await fetch("/api/settings/language");
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.language) {
          setSelectedLanguage(data.language);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/login");
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Settings</CardTitle>
        <CardDescription>Customize your OpenManus experience</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="language">Response Language</Label>
          <Select value={selectedLanguage} onValueChange={handleLanguageChange} disabled={isLoading}>
            <SelectTrigger className="w-full h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md" position="popper" sideOffset={5}>
              {LANGUAGES.map((language) => (
                <SelectItem key={language.code} value={language.code} className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground">
                  {language.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-muted-foreground">
            Choose the language for AI responses. This setting affects how the AI formats its answers.
          </p>
          {/* Debug information */}
          <div className="text-xs text-muted-foreground">
            <p>Selected Language: {selectedLanguage}</p>
            <p>Available Languages: {LANGUAGES.length}</p>
            <p>Component Loaded: true</p>
          </div>
        </div>

        {/* Account Section */}
        <div className="space-y-4 pt-4 border-t border-border">
          <div>
            <h3 className="text-lg font-medium">Account</h3>
            <p className="text-sm text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row sm:justify-end gap-2">
            <Button 
              variant="destructive" 
              onClick={handleLogout}
              className="w-full sm:w-auto"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Log Out
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};