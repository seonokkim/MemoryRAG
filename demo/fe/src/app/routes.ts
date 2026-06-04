import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { HomeScreen } from "./components/HomeScreen";
import { SwingUploadScreen } from "./components/SwingUploadScreen";
import { AnalysisResultScreen } from "./components/AnalysisResultScreen";
import { AIChatScreen } from "./components/AIChatScreen";
import { GolferProfileScreen } from "./components/GolferProfileScreen";
import { PracticeRoutineScreen } from "./components/PracticeRoutineScreen";
import { MonthlyReportScreen } from "./components/MonthlyReportScreen";
import { DevPanelScreen } from "./components/DevPanelScreen";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: HomeScreen },
      { path: "upload", Component: SwingUploadScreen },
      { path: "analysis", Component: AnalysisResultScreen },
      { path: "coach", Component: AIChatScreen },
      { path: "profile", Component: GolferProfileScreen },
      { path: "routine", Component: PracticeRoutineScreen },
      { path: "report", Component: MonthlyReportScreen },
      { path: "dev", Component: DevPanelScreen },
    ],
  },
]);
