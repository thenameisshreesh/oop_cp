#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>

// ================= LOG FUNCTION =================
void logEvent(const std::string& message) {
    SYSTEMTIME st;
    GetLocalTime(&st);

    char buffer[40];
    sprintf(buffer, "%04d-%02d-%02d %02d:%02d:%02d",
        st.wYear, st.wMonth, st.wDay,
        st.wHour, st.wMinute, st.wSecond);

    std::string finalMsg = std::string(buffer) + "  " + message;

    std::cout << finalMsg << std::endl;

    std::ofstream file("tracker_log.txt", std::ios::app);
    if (file.is_open()) {
        file << finalMsg << "\n";
        file.close();
    }
}


std::wstring toWString(const std::string& str) {
    int size_needed = MultiByteToWideChar(CP_ACP, 0, str.c_str(), -1, NULL, 0);
    std::wstring wstr(size_needed, 0);
    MultiByteToWideChar(CP_ACP, 0, str.c_str(), -1, &wstr[0], size_needed);
    return wstr;
}

// ========================================================
// ================= FILE & FOLDER TRACKING MODE ===================
// ========================================================
void fileTracking() {
    system("cls");
    std::cout << "============================\n";
    std::cout << "  ADVANCED FILE TRACKER\n";
    std::cout << "============================\n";
    std::cout << "Enter full file path to track:\n";

    std::string filePath;
    std::getline(std::cin, filePath);

    std::wstring wFilePath = toWString(filePath);

    WIN32_FILE_ATTRIBUTE_DATA fileInfo;
    bool fileExists = GetFileAttributesExW(
        wFilePath.c_str(), GetFileExInfoStandard, &fileInfo
    );

    ULONGLONG lastSize = 0;
    FILETIME lastWriteTime = {};

    if (fileExists) {
        logEvent("[OK] File tracking started: " + filePath);
        lastSize = ((ULONGLONG)fileInfo.nFileSizeHigh << 32) | fileInfo.nFileSizeLow;
        lastWriteTime = fileInfo.ftLastWriteTime;
    }
    else {
        logEvent("[WAITING] File does not exist. Waiting...");
    }

    while (true) {
        Sleep(1000);

        bool existsNow = GetFileAttributesExW(
            wFilePath.c_str(), GetFileExInfoStandard, &fileInfo
        );

        if (!fileExists && existsNow) {
            logEvent("[CREATED] File created: " + filePath);
            fileExists = true;
            lastWriteTime = fileInfo.ftLastWriteTime;
            lastSize = ((ULONGLONG)fileInfo.nFileSizeHigh << 32) | fileInfo.nFileSizeLow;
        }
        else if (fileExists && !existsNow) {
            logEvent("[DELETED] File deleted: " + filePath);
            fileExists = false;
        }
        else if (fileExists && existsNow) {
            ULONGLONG currentSize =
                ((ULONGLONG)fileInfo.nFileSizeHigh << 32) | fileInfo.nFileSizeLow;

            FILETIME currentWriteTime = fileInfo.ftLastWriteTime;

            if (CompareFileTime(&currentWriteTime, &lastWriteTime) != 0 ||
                currentSize != lastSize) {
                logEvent("[MODIFIED] File modified: " + filePath);
                lastWriteTime = currentWriteTime;
                lastSize = currentSize;
            }
        }

        if (GetAsyncKeyState('Q') & 0x8000) {
            logEvent("[EXIT] File tracking stopped.");
            Sleep(1000);
            return;
        }
    }
}

// =========================================================
// ================= FOLDER TRACKING MODE =================
// =========================================================
void folderTracking() {
    system("cls");
    std::cout << "============================\n";
    std::cout << "  ADVANCED FOLDER TRACKER\n";
    std::cout << "============================\n";
    std::cout << "Enter full folder path to track:\n";

    std::string folderPath;
    std::getline(std::cin, folderPath);

    std::wstring wFolderPath = toWString(folderPath);

    HANDLE hDir = CreateFileW(
        wFolderPath.c_str(),
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        NULL
    );

    if (hDir == INVALID_HANDLE_VALUE) {
        logEvent("[ERROR] Could not open folder!");
        Sleep(2000);
        return;
    }

    logEvent("[OK] Folder tracking started: " + folderPath);

    char buffer[2048];
    DWORD bytesReturned;

    // ✅ ANTI-REPEAT SYSTEM (MINGW SAFE)
    std::string lastFile = "";
    DWORD lastAction = 0;
    DWORD lastTime = 0;

    while (true) {
        ReadDirectoryChangesW(
            hDir,
            &buffer,
            sizeof(buffer),
            TRUE,
            FILE_NOTIFY_CHANGE_FILE_NAME |
            FILE_NOTIFY_CHANGE_DIR_NAME |
            FILE_NOTIFY_CHANGE_SIZE |
            FILE_NOTIFY_CHANGE_LAST_WRITE,
            &bytesReturned,
            NULL,
            NULL
        );

        FILE_NOTIFY_INFORMATION* info = (FILE_NOTIFY_INFORMATION*)buffer;

        do {
            std::wstring fileName(info->FileName, info->FileNameLength / sizeof(WCHAR));
            std::string file(fileName.begin(), fileName.end());

            if (file == "tracker_log.txt")
                continue;

            DWORD now = GetTickCount();   // ✅ FIXED FOR MINGW

            if (file == lastFile &&
                info->Action == lastAction &&
                (now - lastTime) < 1500)
                goto SKIP_EVENT;

            lastFile = file;
            lastAction = info->Action;
            lastTime = now;

            switch (info->Action) {
            case FILE_ACTION_ADDED:
                logEvent("[FOLDER] File Created: " + file);
                break;
            case FILE_ACTION_REMOVED:
                logEvent("[FOLDER] File Deleted: " + file);
                break;
            case FILE_ACTION_MODIFIED:
                logEvent("[FOLDER] File Modified: " + file);
                break;
            case FILE_ACTION_RENAMED_OLD_NAME:
                logEvent("[FOLDER] Rename Old: " + file);
                break;
            case FILE_ACTION_RENAMED_NEW_NAME:
                logEvent("[FOLDER] Rename New: " + file);
                break;
            }

        SKIP_EVENT:

            if (info->NextEntryOffset == 0)
                break;

            info = (FILE_NOTIFY_INFORMATION*)((char*)info + info->NextEntryOffset);

        } while (true);

        if (GetAsyncKeyState('Q') & 0x8000) {
            logEvent("[EXIT] Folder tracking stopped.");
            CloseHandle(hDir);
            Sleep(1000);
            return;
        }
    }
}

// ========================================================
// ========================= MAIN MENU ====================
// ========================================================
int main() {
    while (true) {
        system("cls");
        std::cout << "==============================\n";
        std::cout << "  ADVANCED TRACKING SYSTEM\n";
        std::cout << "==============================\n";
        std::cout << "1. Track Folder\n";
        std::cout << "2. Track File\n";
        std::cout << "3. Exit\n";
        std::cout << "Enter choice: ";

        int choice;
        std::cin >> choice;
        std::cin.ignore();

        switch (choice) {
        case 1:
            folderTracking();
            break;
        case 2:
            fileTracking();
            break;
        case 3:
            logEvent("[EXIT] Program terminated.");
            exit(0);
        default:
            std::cout << "Invalid choice!\n";
            Sleep(1500);
        }
    }
}
