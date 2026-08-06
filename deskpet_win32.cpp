// 小海桌宠 - Windows Desktop Pet
// Cross-compile: x86_64-w64-mingw32-g++ -static -static-libgcc -static-libstdc++ -mwindows -o 小海桌宠.exe deskpet_win32.cpp -lgdiplus -lshlwapi -lcomctl32 -luxtheme -lwinmm -mms-bitfields
// Or compile with MSVC: cl deskpet_win32.cpp /std:c++17 /EHsc /link gdiplus.lib shlwapi.lib comctl32.lib uxtheme.lib winmm.lib /SUBSYSTEM:WINDOWS

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <gdiplus.h>
#include <commctrl.h>
#include <uxtheme.h>
#include <dwmapi.h>
#include <shlwapi.h>
#include <shellapi.h>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <cmath>

#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "uxtheme.lib")
#pragma comment(lib, "dwmapi.lib")
#pragma comment(lib, "winmm.lib")

using namespace Gdiplus;
using namespace std;

// ============================================================
// Configuration
// ============================================================
#define APP_NAME L"小海桌宠"
#define WINDOW_CLASS L"XiaoHaiDeskPet"
#define DEFAULT_WIDTH 200
#define DEFAULT_HEIGHT 200
#define MIN_SIZE 50
#define MAX_SIZE 500
#define ANIMATION_TIMER 1
#define BUBBLE_TIMER 2
#define WALK_TIMER 3
#define FOLLOW_TIMER 4
#define SLEEP_TIMER 5

// ============================================================
// Chinese Chat Messages
// ============================================================
const wchar_t* CHAT_MESSAGES[] = {
    L"今天天气真好呀~ ☀️",
    L"嘿嘿，盯着我看干嘛？",
    L"工作好累，想摸鱼🐟",
    L"你回来啦！想你了！",
    L"要不要一起喝杯咖啡？☕",
    L"盯——(●—●)",
    L"我今天是不是很可爱？",
    L"好无聊哦，陪我玩会儿~",
    L"加油加油！你是最棒的！💪",
    L"呼噜噜~ 好困啊😴",
    L"咦？有吃的吗？🍔",
    L"哼哼，我不理你了！",
    L"我最喜欢你了！❤️",
    L"Hello World! 🌍",
    L"摸头杀！(,,´▽`)ノ",
    L"再点我就要跳起来了！",
    L"你工作做完了吗？👀",
    L"今天心情不错~ 🎵",
    L"饿了饿了，投喂投喂！",
    L"我是小海，你的专属桌宠~",
    L"摸摸摸，头都要摸秃了！",
    L"好想出去玩啊 🚀",
    L"代码写完了吗？让我看看",
    L"叮！您的可爱桌宠已上线",
    L"别戳了别戳了！要生气了！",
    L"(｡ˇ‸ˇ｡) 哼！",
    L"今天也要元气满满哦！✨",
    L"呼——好困，想睡觉",
    L"你专注工作的样子真帅！",
    L"我来陪你加班啦~",
};

const wchar_t* FEED_MESSAGES[] = {
    L"好吃好吃！再来一份！🍔",
    L"啊呜~~~~ 真香！",
    L"嗝~ 吃撑了...",
    L"谢谢投喂！爱你！❤️",
    L"这是什么神仙美食！",
    L"再来一口嘛~",
    L"好吃到转圈圈！",
    L"你喂什么我都爱吃！",
};

const wchar_t* TALK_MESSAGES[] = {
    L"今天过得怎么样？😊",
    L"有什么烦恼可以跟我说说~",
    L"你知道海尔的愿景是什么吗？",
    L"人单合一，我是小海~",
    L"要不要听个笑话？",
    L"你猜我今天看到了什么？",
    L"我最喜欢陪你聊天了！",
    L"工作加油，我在这里陪你！",
    L"你知道什么是链群吗？",
    L"海尔智家，定制美好生活~",
};

const wchar_t* PET_MESSAGES[] = {
    L"嘿嘿，好舒服呀~ 😊",
    L"再摸摸嘛~ 好舒服！",
    L"唔...好温暖...",
    L"你手好温柔哦~",
    L"摸摸头会长不高的！",
    L"好喜欢被你摸~ ❤️",
    L"呼噜噜噜~ 像小猫一样",
    L"好幸福的感觉~",
    L"再摸五分钟！",
    L"你要摸到什么时候啦~",
};

// ============================================================
// Animation States
// ============================================================
enum PetState {
    IDLE,
    JUMPING,
    SQUASHING,
    SHAKING,
    PETTING,
    WALKING,
    SLEEPING,
    FEEDING,
    TALKING,
    FOLLOWING
};

enum PetAction {
    ACT_NONE,
    ACT_JUMP,
    ACT_SQUASH,
    ACT_SHAKE,
    ACT_PET,
    ACT_FEED,
    ACT_TALK
};

// ============================================================
// Global Variables
// ============================================================
HWND g_hWnd = NULL;
HINSTANCE g_hInst = NULL;
ULONG_PTR g_gdiplusToken = NULL;
Image* g_petImage = NULL;
Image* g_petImageBG = NULL;

int g_petWidth = DEFAULT_WIDTH;
int g_petHeight = DEFAULT_HEIGHT;
int g_screenW = 0;
int g_screenH = 0;
int g_petX = 100;
int g_petY = 100;
int g_walkTargetX = 100;
int g_walkTargetY = 100;
float g_scale = 1.0f;

bool g_topmost = true;
bool g_dragging = false;
bool g_followMouse = false;
bool g_hasTransparentImage = false;

POINT g_dragStart;
POINT g_petPosStart;
POINT g_cursorPos;

PetState g_state = IDLE;
PetAction g_nextAction = ACT_NONE;
int g_animFrame = 0;
int g_animMaxFrame = 20;
int g_actionTimer = 0;

wstring g_bubbleText = L"";
bool g_showBubble = false;
int g_bubbleTimer = 0;

// Image data - embedded character image (will be replaced by external file)
wstring g_imagePath = L"character.png";

// ============================================================
// Function Declarations
// ============================================================
LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);
void ShowContextMenu(HWND, POINT);
void UpdatePetPosition();
void DrawPet(HDC);
void DrawBubble(HDC);
void StartAnimation(PetAction action);
void DoAnimationStep();
void DoWalkStep();
void DoFollowMouse();
void SetPetState(PetState newState);
void SetBubbleText(const wstring& text, int duration = 3000);
void SetBubbleTextFromArray(const wchar_t* arr[], int count);
void LoadPetImage();
void AdjustSize(int delta);
void ToggleTopmost();
void ExitProgram();
void RandomWalkTarget();
wstring RandomFromArray(const wchar_t* arr[], int count);

// ============================================================
// Image Loading
// ============================================================
void LoadPetImage() {
    // Try to load the character image
    if (g_petImage) { delete g_petImage; g_petImage = NULL; }
    if (g_petImageBG) { delete g_petImageBG; g_petImageBG = NULL; }
    
    // Try PNG first, then JPG
    g_petImage = Image::FromFile(g_imagePath.c_str());
    if (g_petImage->GetLastStatus() != Ok) {
        delete g_petImage;
        g_petImage = NULL;
        // Try .jpg
        wstring jpgPath = L"character.jpg";
        g_petImage = Image::FromFile(jpgPath.c_str());
        if (g_petImage->GetLastStatus() != Ok) {
            delete g_petImage;
            g_petImage = NULL;
        }
    }
    
    // Also load the background version for reference
    g_petImageBG = Image::FromFile(g_imagePath.c_str());
    if (g_petImageBG->GetLastStatus() != Ok) {
        delete g_petImageBG;
        g_petImageBG = NULL;
        wstring jpgPath = L"character.jpg";
        g_petImageBG = Image::FromFile(jpgPath.c_str());
        if (g_petImageBG->GetLastStatus() != Ok) {
            delete g_petImageBG;
            g_petImageBG = NULL;
        }
    }
}

// ============================================================
// Random helpers
// ============================================================
wstring RandomFromArray(const wchar_t* arr[], int count) {
    return arr[rand() % count];
}

// ============================================================
// Bubble Text
// ============================================================
void SetBubbleText(const wstring& text, int duration) {
    g_bubbleText = text;
    g_showBubble = !text.empty();
    g_bubbleTimer = duration;
    InvalidateRect(g_hWnd, NULL, TRUE);
}

void SetBubbleTextFromArray(const wchar_t* arr[], int count) {
    SetBubbleText(RandomFromArray(arr, count));
}

// ============================================================
// Drawing Functions
// ============================================================
void DrawPet(HDC hdc) {
    if (!g_petImage) return;
    
    Graphics graphics(hdc);
    graphics.SetSmoothingMode(SmoothingModeHighQuality);
    graphics.SetInterpolationMode(InterpolationModeHighQualityBicubic);
    
    int w = g_petWidth;
    int h = g_petHeight;
    int drawX = 0, drawY = 0;
    float stretchX = 1.0f, stretchY = 1.0f;
    
    // Apply animation transforms
    switch (g_state) {
        case JUMPING: {
            float progress = (float)g_animFrame / g_animMaxFrame;
            float jumpY = -sin(progress * 3.14159f) * 80 * g_scale;
            drawY = (int)jumpY;
            break;
        }
        case SQUASHING: {
            float progress = (float)g_animFrame / g_animMaxFrame;
            if (progress < 0.3f) {
                stretchX = 1.0f + progress * 0.6f;
                stretchY = 1.0f - progress * 0.4f;
            } else if (progress < 0.6f) {
                float t = (progress - 0.3f) / 0.3f;
                stretchX = 1.6f - t * 0.6f;
                stretchY = 0.6f + t * 0.4f;
            } else {
                float t = (progress - 0.6f) / 0.4f;
                stretchX = 1.0f + (1.0f - t) * 0.1f;
                stretchY = 1.0f;
            }
            break;
        }
        case SHAKING: {
            float shake = sin((float)g_animFrame * 0.8f) * 20 * g_scale;
            drawX = (int)shake;
            break;
        }
        case PETTING: {
            float tilt = sin((float)g_animFrame * 0.3f) * 5;
            stretchX = 1.0f;
            stretchY = 1.0f;
            break;
        }
        case WALKING: {
            float bob = sin((float)g_animFrame * 0.5f) * 5 * g_scale;
            drawY = (int)bob;
            break;
        }
        case SLEEPING: {
            float breath = sin((float)g_animFrame * 0.08f) * 0.03f;
            stretchX = 1.0f + breath;
            stretchY = 1.0f - breath;
            break;
        }
        case FEEDING: {
            float bounce = sin((float)g_animFrame * 0.4f) * 8 * g_scale;
            drawY = (int)bounce;
            break;
        }
        case TALKING: {
            float bounce = sin((float)g_animFrame * 0.2f) * 3 * g_scale;
            drawY = (int)bounce;
            break;
        }
    }
    
    // Draw the image with transforms
    int imgW = g_petImage->GetWidth();
    int imgH = g_petImage->GetHeight();
    
    // Scale to fit the pet window
    float scaleX = (float)w / imgW * stretchX;
    float scaleY = (float)h / imgH * stretchY;
    float scale = min(scaleX, scaleY);
    
    int drawW = (int)(imgW * scale);
    int drawH = (int)(imgH * scale);
    int offsetX = (w - drawW) / 2 + drawX;
    int offsetY = (h - drawH) / 2 + drawY;
    
    // For walking animation, slightly shift
    if (g_state == WALKING) {
        offsetX += (int)(sin((float)g_animFrame * 0.2f) * 5);
    }
    
    Rect destRect(offsetX, offsetY, drawW, drawH);
    graphics.DrawImage(g_petImage, destRect, 0, 0, imgW, imgH, UnitPixel);
    
    // Draw sleep Z's
    if (g_state == SLEEPING) {
        Font font(L"Arial", 20 * g_scale, FontStyleBold);
        SolidBrush brush(Color(180, 100, 150, 255));
        StringFormat format;
        format.SetAlignment(StringAlignmentCenter);
        
        float zOffset = sin((float)g_animFrame * 0.05f) * 10;
        PointF zPos((float)(w - 30), (float)(10 + zOffset));
        graphics.DrawString(L"Z", -1, &font, zPos, &format, &brush);
        
        zOffset = sin((float)(g_animFrame + 10) * 0.05f) * 12;
        zPos = PointF((float)(w - 50), (float)(-5 + zOffset));
        graphics.DrawString(L"Z", -1, &font, &brush, zPos.x, zPos.y);
        
        zOffset = sin((float)(g_animFrame + 20) * 0.05f) * 15;
        zPos = PointF((float)(w - 70), (float)(-20 + zOffset));
        graphics.DrawString(L"Z", -1, &font, &brush, zPos.x, zPos.y);
    }
    
    // Draw heart for petting
    if (g_state == PETTING && (g_animFrame % 10 < 5)) {
        Font font(L"Segoe UI Emoji", 16 * g_scale);
        SolidBrush heartBrush(Color(200, 255, 50, 100));
        PointF heartPos((float)(w - 40), (float)(10));
        graphics.DrawString(L"❤️", -1, &font, heartPos, &format, &heartBrush);
    }
}

void DrawBubble(HDC hdc) {
    if (!g_showBubble || g_bubbleText.empty()) return;
    
    Graphics graphics(hdc);
    graphics.SetSmoothingMode(SmoothingModeHighQuality);
    
    Font font(L"Microsoft YaHei", 14 * g_scale, FontStyleRegular);
    RectF textRect;
    graphics.MeasureString(g_bubbleText.c_str(), -1, &font, PointF(0, 0), &textRect);
    
    float padding = 12 * g_scale;
    float bubbleW = textRect.Width + padding * 2;
    float bubbleH = textRect.Height + padding * 2;
    float maxBubbleW = (float)g_petWidth * 2.5f;
    if (bubbleW > maxBubbleW) {
        bubbleW = maxBubbleW;
        // Re-measure with wrapping
        RectF wrapRect(0, 0, bubbleW - padding * 2, 1000);
        graphics.MeasureString(g_bubbleText.c_str(), -1, &font, wrapRect, &textRect);
        bubbleH = textRect.Height + padding * 2;
    }
    
    float bubbleX = (g_petWidth - bubbleW) / 2;
    float bubbleY = -bubbleH - 15 * g_scale;
    
    // Ensure bubble is visible (not off-screen)
    if (bubbleY < 0) bubbleY = 0;
    
    // Draw bubble background
    SolidBrush bgBrush(Color(230, 255, 255, 255));
    SolidBrush borderBrush(Color(180, 200, 200, 200));
    Pen borderPen(&borderBrush, 2.0f);
    
    GraphicsPath path;
    path.AddRoundRect(RectF(bubbleX, bubbleY, bubbleW, bubbleH), 10 * g_scale);
    
    graphics.FillPath(&bgBrush, &path);
    graphics.DrawPath(&borderPen, &path);
    
    // Draw triangle pointer
    PointF triangle[3];
    float triSize = 8 * g_scale;
    float centerX = g_petWidth / 2.0f;
    triangle[0] = PointF(centerX - triSize, bubbleY + bubbleH);
    triangle[1] = PointF(centerX + triSize, bubbleY + bubbleH);
    triangle[2] = PointF(centerX, bubbleY + bubbleH + triSize * 1.5f);
    graphics.FillPolygon(&bgBrush, triangle, 3);
    graphics.DrawLine(&borderPen, triangle[0], triangle[2]);
    graphics.DrawLine(&borderPen, triangle[2], triangle[1]);
    
    // Draw text
    SolidBrush textBrush(Color(50, 50, 50));
    StringFormat format;
    format.SetAlignment(StringAlignmentCenter);
    format.SetLineAlignment(StringAlignmentCenter);
    RectF textRect2(bubbleX + padding, bubbleY + padding, bubbleW - padding * 2, bubbleH - padding * 2);
    graphics.DrawString(g_bubbleText.c_str(), -1, &font, textRect2, &format, &textBrush);
}

// ============================================================
// Animation Control
// ============================================================
void StartAnimation(PetAction action) {
    g_nextAction = action;
    g_animFrame = 0;
    g_animMaxFrame = 20;
    g_actionTimer = 0;
    
    switch (action) {
        case ACT_JUMP:
            SetPetState(JUMPING);
            g_animMaxFrame = 25;
            SetBubbleText(L"呀呼~~ 跳起来！🦘");
            break;
        case ACT_SQUASH:
            SetPetState(SQUASHING);
            g_animMaxFrame = 20;
            SetBubbleText(L"哎呀！被压扁了🤪");
            break;
        case ACT_SHAKE:
            SetPetState(SHAKING);
            g_animMaxFrame = 30;
            SetBubbleText(L"不要不要！好晕啊🌀");
            break;
        case ACT_PET:
            SetPetState(PETTING);
            g_animMaxFrame = 40;
            SetBubbleTextFromArray(PET_MESSAGES, 10);
            break;
        case ACT_FEED:
            SetPetState(FEEDING);
            g_animMaxFrame = 30;
            SetBubbleTextFromArray(FEED_MESSAGES, 8);
            break;
        case ACT_TALK:
            SetPetState(TALKING);
            g_animMaxFrame = 30;
            SetBubbleTextFromArray(TALK_MESSAGES, 10);
            break;
    }
    
    SetTimer(g_hWnd, ANIMATION_TIMER, 50, NULL);
}

void DoAnimationStep() {
    g_animFrame++;
    
    if (g_animFrame >= g_animMaxFrame) {
        // Animation complete
        if (g_state == PETTING) {
            SetBubbleText(L"嘿嘿~ 好舒服😊");
        }
        KillTimer(g_hWnd, ANIMATION_TIMER);
        SetPetState(IDLE);
        return;
    }
    
    InvalidateRect(g_hWnd, NULL, TRUE);
}

void DoWalkStep() {
    if (g_state != WALKING && g_state != IDLE) return;
    
    if (g_state == WALKING) {
        g_animFrame++;
        
        // Move towards target
        int dx = g_walkTargetX - g_petX;
        int dy = g_walkTargetY - g_petY;
        float dist = sqrt((float)(dx*dx + dy*dy));
        
        if (dist < 10) {
            // Reached target, stay idle for a bit
            SetPetState(IDLE);
            SetBubbleText(L"到站啦~ 🚏");
            KillTimer(g_hWnd, WALK_TIMER);
            return;
        }
        
        float speed = 3.0f * g_scale;
        g_petX += (int)(dx / dist * speed);
        g_petY += (int)(dy / dist * speed);
        
        UpdatePetPosition();
        InvalidateRect(g_hWnd, NULL, TRUE);
    }
}

void DoFollowMouse() {
    POINT pt;
    GetCursorPos(&pt);
    
    if (!g_followMouse) {
        KillTimer(g_hWnd, FOLLOW_TIMER);
        return;
    }
    
    int dx = pt.x - g_petX - g_petWidth/2;
    int dy = pt.y - g_petY - g_petHeight/2;
    float dist = sqrt((float)(dx*dx + dy*dy));
    
    if (dist > 50) {
        float speed = 8.0f * g_scale;
        g_petX += (int)(dx / dist * speed);
        g_petY += (int)(dy / dist * speed);
        g_animFrame++;
        SetPetState(WALKING);
        UpdatePetPosition();
        InvalidateRect(g_hWnd, NULL, TRUE);
    } else {
        if (g_state == WALKING) {
            SetPetState(IDLE);
        }
    }
}

void SetPetState(PetState newState) {
    if (g_state == newState) return;
    g_state = newState;
    g_animFrame = 0;
    InvalidateRect(g_hWnd, NULL, TRUE);
}

void RandomWalkTarget() {
    RECT workArea;
    SystemParametersInfo(SPI_GETWORKAREA, 0, &workArea, 0);
    
    g_walkTargetX = workArea.left + (rand() % (workArea.right - workArea.left - g_petWidth));
    g_walkTargetY = workArea.top + (rand() % (workArea.bottom - workArea.top - g_petHeight));
    
    g_animFrame = 0;
    SetPetState(WALKING);
    g_bubbleText = L"出去溜达溜达~ 🚶";
    g_showBubble = true;
    g_bubbleTimer = 2000;
    
    SetTimer(g_hWnd, WALK_TIMER, 30, NULL);
}

// ============================================================
// Window Management
// ============================================================
void UpdatePetPosition() {
    SetWindowPos(g_hWnd, g_topmost ? HWND_TOPMOST : HWND_NOTOPMOST,
                 g_petX, g_petY, g_petWidth, g_petHeight,
                 SWP_NOACTIVATE | SWP_SHOWWINDOW);
}

void AdjustSize(int delta) {
    g_scale += delta * 0.05f;
    if (g_scale < 0.3f) g_scale = 0.3f;
    if (g_scale > 3.0f) g_scale = 3.0f;
    
    g_petWidth = (int)(DEFAULT_WIDTH * g_scale);
    g_petHeight = (int)(DEFAULT_HEIGHT * g_scale);
    
    UpdatePetPosition();
    InvalidateRect(g_hWnd, NULL, TRUE);
}

void ToggleTopmost() {
    g_topmost = !g_topmost;
    SetWindowPos(g_hWnd, g_topmost ? HWND_TOPMOST : HWND_NOTOPMOST,
                 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
}

void ExitProgram() {
    DestroyWindow(g_hWnd);
}

// ============================================================
// Right-click Context Menu
// ============================================================
void ShowContextMenu(HWND hWnd, POINT pt) {
    HMENU hMenu = CreatePopupMenu();
    
    AppendMenu(hMenu, MF_STRING, 1001, L"💬 陪我聊聊天");
    AppendMenu(hMenu, MF_STRING, 1002, L"🤚 摸摸头");
    AppendMenu(hMenu, MF_STRING, 1003, L"🍔 喂吃的");
    AppendMenu(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenu(hMenu, MF_STRING, 1004, L"🚶 让她走路");
    AppendMenu(hMenu, MF_STRING, 1005, L"💤 让她睡觉");
    AppendMenu(hMenu, MF_STRING, 1006, L"🖱️ 跟随鼠标");
    AppendMenu(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenu(hMenu, MF_STRING, 1007, L"📏 调整大小");
    AppendMenu(hMenu, MF_STRING | (g_topmost ? MF_CHECKED : 0), 1008, L"📌 置顶开关");
    AppendMenu(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenu(hMenu, MF_STRING, 1009, L"❌ 退出程序");
    
    // Size submenu
    HMENU hSizeMenu = CreatePopupMenu();
    AppendMenu(hSizeMenu, MF_STRING, 1010, L"🔍 放大");
    AppendMenu(hSizeMenu, MF_STRING, 1011, L"🔎 缩小");
    AppendMenu(hSizeMenu, MF_STRING, 1012, L"1:1 原始大小");
    ModifyMenu(hMenu, 1007, MF_BYCOMMAND | MF_POPUP, (UINT_PTR)hSizeMenu, L"📏 调整大小");
    
    // Follow mouse submenu
    HMENU hFollowMenu = CreatePopupMenu();
    AppendMenu(hFollowMenu, MF_STRING | (g_followMouse ? MF_CHECKED : 0), 1013, L"🖱️ 开启跟随鼠标");
    ModifyMenu(hMenu, 1006, MF_BYCOMMAND | MF_POPUP, (UINT_PTR)hFollowMenu, L"🖱️ 跟随鼠标");
    
    SetForegroundWindow(hWnd);
    int cmd = TrackPopupMenu(hMenu, TPM_RETURNCMD | TPM_NONOTIFY, pt.x, pt.y, 0, hWnd, NULL);
    DestroyMenu(hMenu);
    
    switch (cmd) {
        case 1001: // Talk
            StartAnimation(ACT_TALK);
            break;
        case 1002: // Pet
            StartAnimation(ACT_PET);
            break;
        case 1003: // Feed
            StartAnimation(ACT_FEED);
            break;
        case 1004: // Walk
            RandomWalkTarget();
            break;
        case 1005: // Sleep
            SetPetState(SLEEPING);
            SetBubbleText(L"zzz... 晚安💤");
            SetTimer(g_hWnd, SLEEP_TIMER, 100, NULL);
            break;
        case 1006: // Follow mouse
            g_followMouse = !g_followMouse;
            if (g_followMouse) {
                SetTimer(g_hWnd, FOLLOW_TIMER, 30, NULL);
                SetBubbleText(L"跟着你走~ 🖱️");
            } else {
                KillTimer(g_hWnd, FOLLOW_TIMER);
                SetPetState(IDLE);
                SetBubbleText(L"不跟了，休息一下~");
            }
            break;
        case 1013: // Toggle follow from submenu
            g_followMouse = !g_followMouse;
            if (g_followMouse) {
                SetTimer(g_hWnd, FOLLOW_TIMER, 30, NULL);
                SetBubbleText(L"跟着你走~ 🖱️");
            } else {
                KillTimer(g_hWnd, FOLLOW_TIMER);
                SetPetState(IDLE);
                SetBubbleText(L"不跟了，休息一下~");
            }
            break;
        case 1010: // Zoom in
            AdjustSize(1);
            break;
        case 1011: // Zoom out
            AdjustSize(-1);
            break;
        case 1012: // Reset size
            g_scale = 1.0f;
            g_petWidth = DEFAULT_WIDTH;
            g_petHeight = DEFAULT_HEIGHT;
            UpdatePetPosition();
            InvalidateRect(g_hWnd, NULL, TRUE);
            SetBubbleText(L"恢复原始大小~");
            break;
        case 1008: // Toggle topmost
            ToggleTopmost();
            break;
        case 1009: // Exit
            ExitProgram();
            break;
    }
}

// ============================================================
// Window Procedure
// ============================================================
LRESULT CALLBACK WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            // Enable translucent window
            SetLayeredWindowAttributes(hWnd, 0, 255, LWA_ALPHA);
            
            // Enable click-through for transparent areas using DWM
            DWM_BLURBEHIND bb = {0};
            bb.dwFlags = DWM_BB_ENABLE | DWM_BB_BLURREGION;
            bb.fEnable = true;
            bb.hRgnBlur = CreateRectRgn(0, 0, -1, -1);
            DwmEnableBlurBehindWindow(hWnd, &bb);
            
            // Load pet image
            LoadPetImage();
            if (!g_petImage) {
                MessageBox(hWnd, L"无法加载角色图片，请确保 character.png 或 character.jpg 存在", L"错误", MB_ICONERROR);
            }
            
            // Set random initial position
            RECT workArea;
            SystemParametersInfo(SPI_GETWORKAREA, 0, &workArea, 0);
            g_petX = workArea.left + 100 + (rand() % (workArea.right - workArea.left - 400));
            g_petY = workArea.top + 100 + (rand() % (workArea.bottom - workArea.top - 400));
            
            // Show welcome message
            SetBubbleText(L"嗨！我是小海桌宠~ 右键点击我有菜单哦！🦦", 5000);
            
            return 0;
        }
        
        case WM_LBUTTONDOWN: {
            g_dragging = true;
            g_dragStart.x = GET_X_LPARAM(lParam);
            g_dragStart.y = GET_Y_LPARAM(lParam);
            g_petPosStart.x = g_petX;
            g_petPosStart.y = g_petY;
            SetCapture(hWnd);
            
            // Stop walk/follow on drag
            if (g_state == WALKING) {
                KillTimer(g_hWnd, WALK_TIMER);
            }
            
            return 0;
        }
        
        case WM_LBUTTONUP: {
            if (g_dragging) {
                g_dragging = false;
                ReleaseCapture();
                
                // Check if it was a click (not drag) - trigger animation cycle
                POINT curPos;
                GetCursorPos(&curPos);
                int dx = curPos.x - (g_petPosStart.x + g_dragStart.x);
                int dy = curPos.y - (g_petPosStart.y + g_dragStart.y);
                int dragDist = (int)sqrt((float)(dx*dx + dy*dy));
                
                if (dragDist < 5) {
                    // It was a click, cycle through animations
                    static int animCycle = 0;
                    animCycle = (animCycle + 1) % 4;
                    switch (animCycle) {
                        case 0: StartAnimation(ACT_JUMP); break;
                        case 1: StartAnimation(ACT_SQUASH); break;
                        case 2: StartAnimation(ACT_SHAKE); break;
                        case 3: StartAnimation(ACT_PET); break;
                    }
                }
            }
            return 0;
        }
        
        case WM_LBUTTONDBLCLK: {
            StartAnimation(ACT_TALK);
            return 0;
        }
        
        case WM_MOUSEMOVE: {
            if (g_dragging) {
                POINT curPos;
                GetCursorPos(&curPos);
                g_petX = g_petPosStart.x + (curPos.x - g_petPosStart.x - g_dragStart.x + g_petWidth/2) - g_petWidth/2;
                g_petY = g_petPosStart.y + (curPos.y - g_petPosStart.y - g_dragStart.y + g_petHeight/2) - g_petHeight/2;
                
                // Show walking animation while dragging
                if (g_state != WALKING) {
                    SetPetState(WALKING);
                }
                g_animFrame++;
                
                SetWindowPos(hWnd, g_topmost ? HWND_TOPMOST : HWND_NOTOPMOST,
                             g_petX, g_petY, 0, 0,
                             SWP_NOSIZE | SWP_NOACTIVATE);
                InvalidateRect(hWnd, NULL, TRUE);
            }
            return 0;
        }
        
        case WM_RBUTTONDOWN: {
            POINT pt;
            GetCursorPos(&pt);
            ShowContextMenu(hWnd, pt);
            return 0;
        }
        
        case WM_MOUSEWHEEL: {
            int delta = GET_WHEEL_DELTA_WPARAM(wParam);
            AdjustSize(delta > 0 ? 1 : -1);
            return 0;
        }
        
        case WM_TIMER: {
            switch (wParam) {
                case ANIMATION_TIMER:
                    DoAnimationStep();
                    break;
                case WALK_TIMER:
                    DoWalkStep();
                    break;
                case FOLLOW_TIMER:
                    DoFollowMouse();
                    break;
                case SLEEP_TIMER:
                    g_animFrame++;
                    if (g_bubbleTimer > 0) {
                        g_bubbleTimer -= 100;
                        if (g_bubbleTimer <= 0) {
                            g_showBubble = false;
                        }
                    }
                    InvalidateRect(hWnd, NULL, TRUE);
                    break;
            }
            return 0;
        }
        
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hWnd, &ps);
            
            // Create off-screen buffer
            HDC memDC = CreateCompatibleDC(hdc);
            HBITMAP memBmp = CreateCompatibleBitmap(hdc, g_petWidth, g_petHeight);
            HBITMAP oldBmp = (HBITMAP)SelectObject(memDC, memBmp);
            
            // Clear with transparent color
            RECT rect = {0, 0, g_petWidth, g_petHeight};
            HBRUSH clearBrush = CreateSolidBrush(RGB(0, 0, 0));
            FillRect(memDC, &rect, clearBrush);
            DeleteObject(clearBrush);
            
            // Draw the pet
            DrawPet(memDC);
            
            // Draw bubble
            DrawBubble(memDC);
            
            // Copy to window with transparency
            BLENDFUNCTION blend = {0};
            blend.BlendOp = AC_SRC_OVER;
            blend.SourceConstantAlpha = 255;
            blend.AlphaFormat = AC_SRC_ALPHA;
            
            AlphaBlend(hdc, 0, 0, g_petWidth, g_petHeight,
                       memDC, 0, 0, g_petWidth, g_petHeight, blend);
            
            SelectObject(memDC, oldBmp);
            DeleteObject(memBmp);
            DeleteDC(memDC);
            
            EndPaint(hWnd, &ps);
            return 0;
        }
        
        case WM_DESTROY: {
            if (g_petImage) delete g_petImage;
            if (g_petImageBG) delete g_petImageBG;
            PostQuitMessage(0);
            return 0;
        }
        
        case WM_CLOSE: {
            DestroyWindow(hWnd);
            return 0;
        }
    }
    
    return DefWindowProc(hWnd, msg, wParam, lParam);
}

// ============================================================
// Entry Point
// ============================================================
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    g_hInst = hInstance;
    srand((unsigned int)time(NULL));
    
    // Initialize GDI+
    GdiplusStartupInput gdiplusStartupInput;
    GdiplusStartup(&g_gdiplusToken, &gdiplusStartupInput, NULL);
    
    // Initialize common controls
    INITCOMMONCONTROLSEX icex = {0};
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icex);
    
    // Register window class
    WNDCLASSEX wc = {0};
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = CS_HREDRAW | CS_VREDRAW | CS_DBLCLKS;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    wc.lpszClassName = WINDOW_CLASS;
    
    if (!RegisterClassEx(&wc)) {
        GdiplusShutdown(g_gdiplusToken);
        return 1;
    }
    
    // Get screen dimensions
    RECT workArea;
    SystemParametersInfo(SPI_GETWORKAREA, 0, &workArea, 0);
    g_screenW = workArea.right - workArea.left;
    g_screenH = workArea.bottom - workArea.top;
    
    // Create layered window
    g_hWnd = CreateWindowEx(
        WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_TOPMOST,
        WINDOW_CLASS,
        APP_NAME,
        WS_POPUP,
        g_petX, g_petY, g_petWidth, g_petHeight,
        NULL, NULL, hInstance, NULL
    );
    
    if (!g_hWnd) {
        GdiplusShutdown(g_gdiplusToken);
        return 1;
    }
    
    // Enable transparency via DWM
    DWM_BLURBEHIND bb = {0};
    bb.dwFlags = DWM_BB_ENABLE;
    bb.fEnable = true;
    bb.hRgnBlur = NULL;
    DwmEnableBlurBehindWindow(g_hWnd, &bb);
    
    // Set to topmost
    SetWindowPos(g_hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
    
    // Center the window initially
    g_petX = (g_screenW - g_petWidth) / 2;
    g_petY = (g_screenH - g_petHeight) / 2;
    SetWindowPos(g_hWnd, NULL, g_petX, g_petY, g_petWidth, g_petHeight, SWP_NOZORDER | SWP_NOACTIVATE);
    
    ShowWindow(g_hWnd, nCmdShow);
    UpdateWindow(g_hWnd);
    
    // Run message loop
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    GdiplusShutdown(g_gdiplusToken);
    return (int)msg.wParam;
}