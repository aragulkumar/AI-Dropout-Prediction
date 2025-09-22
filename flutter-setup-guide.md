# Flutter Mobile App Setup Guide

This guide will walk you through setting up the Flutter mobile application for the AI-Based Student Dropout Prediction System, based on the project structure you provided.

---

## Prerequisites

1.  **Flutter SDK**: Make sure you have Flutter installed. You can follow the official [Flutter installation guide](https://flutter.dev/docs/get-started/install).
2.  **An IDE**: Visual Studio Code with the Flutter extension, or Android Studio.
3.  **A running backend**: The Django backend should be running, typically on `http://localhost:8000`.

---

## Step 1: Create the Flutter Project

Navigate to your main project directory (e.g., `ai-dropout-prediction/`). It is best practice to keep your web, mobile, and backend projects in separate, parallel folders.

Your final project structure should look like this:
```
/ai-dropout-prediction
├── /backend      (Your Django project)
├── /frontend     (Your React project)
└── /dropout_prediction_mobile   (Your new Flutter project)
```

To achieve this, open your terminal in the root `ai-dropout-prediction` directory and run the following command. It will create the new `dropout_prediction_mobile` folder for your app.

```bash
# Make sure you are in your main project folder (e.g., /ai-dropout-prediction)
# This command creates a new directory for your mobile app inside it
flutter create dropout_prediction_mobile

# Navigate into the new mobile app directory
cd dropout_prediction_mobile
```

---

## Step 2: Create the Directory Structure

Inside the `lib/` directory of your new project, create the folders outlined in your project structure.

```bash
# Make sure you are in the root of your flutter project

# Remove the default main.dart
rm lib/main.dart

# Create the directory structure
mkdir -p lib/models lib/services lib/screens/auth lib/screens/student lib/screens/teacher lib/screens/common lib/widgets lib/providers lib/utils
```

This structure helps organize your code:
-   `models/`: For your data classes (e.g., `Student`, `User`).
-   `services/`: For API communication (e.g., `ApiService`, `AuthService`).
-   `screens/`: For the main pages of your app, organized by user role.
-   `widgets/`: For reusable UI components (e.g., `RiskIndicator`).
-   `providers/`: For state management using Provider or Riverpod.
-   `utils/`: For helper functions and constants.

---

## Step 3: Add Dependencies

Open your `pubspec.yaml` file and add the following dependencies. These are based on the tech stack outlined in the project documentation.

```yaml
dependencies:
  flutter:
    sdk: flutter

  # For API calls
  dio: ^5.3.3

  # For state management (choose one)
  provider: ^6.0.5
  # or
  # flutter_riverpod: ^2.4.5

  # For data visualization/charts
  fl_chart: ^0.64.0

  # For local storage
  shared_preferences: ^2.2.2

  # For push notifications (optional for now)
  # firebase_core: ^2.17.0
  # firebase_messaging: ^14.6.9

  # For UI icons
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
```

After adding the dependencies, run `flutter pub get` in your terminal to install them.

---

## Step 4: Configure API Connection

Create a file in `lib/utils/` to store your API configuration.

**File: `lib/utils/constants.dart`**
```dart
class ApiConstants {
  static const String baseUrl = 'http://localhost:8000/api';
  // For Android emulator, use 'http://10.0.2.2:8000/api'
  // For iOS simulator, use 'http://localhost:8000/api'
}
```

---

## Step 5: Create a Basic App Entry Point

Create a new `main.dart` file in the `lib/` directory with some basic boilerplate to get you started.

**File: `lib/main.dart`**
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/auth/login_screen.dart'; // You will create this screen next

// Example provider (create this in lib/providers/auth_provider.dart)
class AuthProvider with ChangeNotifier {
  // Your authentication logic will go here
}

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        // Add other providers here
      ],
      child: MaterialApp(
        title: 'Dropout Prediction',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: LoginScreen(), // Set the initial screen
      ),
    );
  }
}
```

You will also need to create the placeholder `LoginScreen`.

**File: `lib/screens/auth/login_screen.dart`**
```dart
import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: const Center(
        child: Text('Login Screen'),
      ),
    );
  }
}
```

---

## Step 6: Run the Application

Now you can run your app on a simulator, emulator, or physical device.

```bash
flutter run
```

You now have a solid foundation for your Flutter mobile app. You can start building out the UI for the login screen, creating your data models, and implementing the API services to connect to the backend.
