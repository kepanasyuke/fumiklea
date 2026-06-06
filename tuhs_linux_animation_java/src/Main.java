import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.net.URI;
import java.util.Random;

public class Main extends JFrame {

    // Световая палитра оригинального монохромного монитора IBM 5151
    private static final Color CRT_BG = new Color(12, 18, 12);           // Угольно-зеленый глубокий фон
    private static final Color PHOSPHOR_BRIGHT = new Color(51, 255, 102); // Пиковое свечение активной строки
    private static final Color PHOSPHOR_DIM = new Color(25, 140, 50);     // Приглушенный тон для неактивных рамок

    private JTextArea terminalArea;
    private JButton actionButton;
    private JButton tuhsButton;

    private Timer animationTimer;
    private int currentStage = 0;
    private int charIndex = 0;
    private String currentText = "";

    // Переменные физической геометрии дисковода 3.5" (CHS-адресация)
    private int cylinder = 0;
    private int head = 0;
    private int sector = 1;
    private final int MAX_CYLINDERS = 40;
    private final Random random = new Random();

    // Буфер для скрытого отслеживания ввода секретного слова "freax"
    private StringBuilder easterEggBuffer = new StringBuilder();

    // Кадры покадровой ASCII-анимации пингвина (Строго одинаковая визуальная длина строк)
    private static final String[][] TUX_FRAMES = {
            {
                    "     _nnnn_     ",
                    "    /      \\    ",
                    "   |  O  O  |   ",
                    "   |   --   |   ",
                    "  //  \\__/  \\\\  ",
                    " //          \\\\ ",
                    " | \\        / | ",
                    "  \\\\________//  ",
                    "   /________\\   "
            },
            {
                    "     _nnnn_     ",
                    "    /      \\    ",
                    "   |  -  -  |   ",
                    "   |   --   |   ",
                    "  ( \\ \\__/ / )  ",
                    "   \\        /   ",
                    "   | \\    / |   ",
                    "   |________|   ",
                    "   /________\\   "
            }
    };

    private int tuxFrameIndex = 0;
    private Timer tuxTimer;

    public Main() {
        setTitle("FreaX Archeox Terminal v1.91");
        setSize(640, 480); // Классическое прямоугольное разрешение старых ЭЛТ-мониторов
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        getContentPane().setBackground(CRT_BG);
        setLayout(new BorderLayout(8, 8));

        // Эмуляция экрана VT100
        terminalArea = new JTextArea();
        terminalArea.setBackground(CRT_BG);
        terminalArea.setForeground(PHOSPHOR_BRIGHT);
        terminalArea.setCaretColor(PHOSPHOR_BRIGHT);
        terminalArea.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        terminalArea.setEditable(false);
        terminalArea.setMargin(new Insets(14, 14, 14, 14));
        terminalArea.setFocusable(false); // Управление клавишами берет на себя окно

        JScrollPane scrollPane = new JScrollPane(terminalArea);
        scrollPane.setBorder(BorderFactory.createLineBorder(PHOSPHOR_DIM, 2));
        add(scrollPane, BorderLayout.CENTER);

        // Панель управления в стиле Norton Commander
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 5));
        panel.setBackground(CRT_BG);

        actionButton = createRetroButton("F5_BOOT_FLOPPY");
        tuhsButton = createRetroButton("F8_OPEN_TUHS_NET");

        panel.add(actionButton);
        panel.add(tuhsButton);
        add(panel, BorderLayout.SOUTH);

        // Таймер для эффекта телетайпа (посимвольный вывод)
        animationTimer = new Timer(15, e -> handleTextAnimation());

        actionButton.addActionListener(e -> startArchaeology());
        tuhsButton.addActionListener(e -> openTuhsWeb());

        showBootSplash();
        initGlobalKeyDispatcher(); // Запуск железного перехватчика
    }

    // Низкоуровневый перехват клавиш на уровне оконного менеджера Java
    private void initGlobalKeyDispatcher() {
        KeyboardFocusManager.getCurrentKeyboardFocusManager().addKeyEventDispatcher(new KeyEventDispatcher() {
            @Override
            public boolean dispatchKeyEvent(KeyEvent e) {
                if (e.getID() == KeyEvent.KEY_PRESSED) {
                    char keyChar = Character.toLowerCase(e.getKeyChar());
                    int keyCode = e.getKeyCode();

                    // Проверка секретного ввода "freax"
                    if ("freax".indexOf(keyChar) != -1) {
                        easterEggBuffer.append(keyChar);
                        if (easterEggBuffer.toString().endsWith("freax")) {
                            triggerSecretEasterEgg();
                            easterEggBuffer.setLength(0);
                            return true;
                        }
                    } else if (keyChar != '\u0000' && keyCode != KeyEvent.VK_F5 && keyCode != KeyEvent.VK_F8) {
                        easterEggBuffer.setLength(0);
                    }

                    // Интерактивный опрос Y/N (Stage 3)
                    if (currentStage == 3) {
                        if (keyChar == 'y') {
                            terminalArea.append("Y\n  [REDIRECTING] Opening hyper-link...");
                            Toolkit.getDefaultToolkit().beep();
                            currentStage = 4;
                            actionButton.setEnabled(true);
                            actionButton.setText("F5_RE_RUN_EMULATION");
                            openTuhsWeb();
                            return true;
                        } else if (keyChar == 'n') {
                            terminalArea.append("N\n  [ABORT] Staying in local environment.\n\nretro-kernel@tuhs:~$ ");
                            currentStage = 4;
                            actionButton.setEnabled(true);
                            actionButton.setText("F5_RE_RUN_EMULATION");
                            return true;
                        }
                    }

                    // Стандартные горячие клавиши F5 и F8
                    if (currentStage != 3) {
                        if (keyCode == KeyEvent.VK_F5 && actionButton.isEnabled()) {
                            startArchaeology();
                            return true;
                        } else if (keyCode == KeyEvent.VK_F8) {
                            openTuhsWeb();
                            return true;
                        }
                    }
                }
                return false;
            }
        });
    }

    private void showBootSplash() {
        terminalArea.setText(
                "========================================================\n" +
                        "  TUHS ARCHIVE SUBSYSTEM // EMULATION: VT100 CRT\n" +
                        "  READY TO EMULATE LINUS TORVALDS' ORIGINAL HARDWARE\n" +
                        "========================================================\n" +
                        "  Target: 3.5\" Floppy Disk Image (Linux v0.01)\n" +
                        "  \n" +
                        "  Клавиатура активна автоматически при старте!\n" +
                        "  \n" +
                        "  Нажмите [F5] на клавиатуре для чтения виртуальной дискеты...\n" +
                        "  Нажмите [F8] на клавиатуре для перехода на сайт TUHS...\n" +
                        "  (Секрет: введите слово 'freax' в любой момент для пасхалки)\n"
        );
    }

    private void startArchaeology() {
        actionButton.setEnabled(false);
        if (tuxTimer != null && tuxTimer.isRunning()) tuxTimer.stop();
        terminalArea.setText("");
        currentStage = 0;
        cylinder = 0;
        head = 0;
        sector = 1;
        executeStage();
    }

    private void executeStage() {
        if (currentStage == 0) {
            currentText = "  [INIT] Connecting to TUHS historical server...\n" +
                    "  [INIT] Mounting virtual raw image: /dev/fd0\n" +
                    "  [WARN] Booting raw 80386 protected mode kernel.\n\n" +
                    "  >> COMMENCING MECHANICAL TRACK READING:\n";
            charIndex = 0;
            animationTimer.start();
        }
        else if (currentStage == 1) {
            animationTimer.stop();
            runMechanicalFloppyRead();
        }
        else if (currentStage == 2) {
            triggerHistoricalPayload();
        }
    }

    private void runMechanicalFloppyRead() {
        Timer floppyTimer = new Timer(30, null);
        floppyTimer.addActionListener(new ActionListener() {
            private int retryCount = 0;

            @Override
            public void actionPerformed(ActionEvent e) {
                if (currentStage == 99) {
                    floppyTimer.stop();
                    return;
                }

                if (cylinder < MAX_CYLINDERS) {
                    String text = terminalArea.getText();
                    int lastLineIdx = text.lastIndexOf("  [SEEK]");
                    if (lastLineIdx != -1) terminalArea.setText(text.substring(0, lastLineIdx));

                    // Случайный сбой магнитного слоя дискеты
                    if (random.nextInt(35) == 0 && retryCount < 2) {
                        retryCount++;
                        floppyTimer.setDelay(400);
                        Toolkit.getDefaultToolkit().beep(); // Звук динамика ПК
                        terminalArea.append("  [SEEK] C:" + cylinder + " H:" + head + " S:" + sector + " -> [!] CRC SECTOR ERROR. RETRYING...\n");
                        return;
                    }

                    retryCount = 0;

                    // Шкала прогресса треков
                    StringBuilder sb = new StringBuilder("  [SEEK] Tracks: [");
                    int progress = (cylinder * 20) / MAX_CYLINDERS;
                    for (int i = 0; i < 20; i++) {
                        if (i < progress) sb.append("■");
                        else if (i == progress) sb.append("►");
                        else sb.append(".");
                    }
                    sb.append(String.format("] C:%02d H:%d S:%02d OK", cylinder, head, sector));
                    terminalArea.append(sb.toString());

                    sector += 3;
                    if (sector > 18) {
                        sector = 1;
                        head++;
                        if (head > 1) {
                            head = 0;
                            cylinder++;
                            floppyTimer.setDelay(140); // Задержка перемещения каретки дисковода
                        }
                    } else {
                        floppyTimer.setDelay(15);
                    }
                } else {
                    floppyTimer.stop();
                    currentStage = 2;
                    executeStage();
                }
            }
        });
        floppyTimer.start();
    }

    private void triggerSecretEasterEgg() {
        animationTimer.stop();
        if (tuxTimer != null && tuxTimer.isRunning()) tuxTimer.stop();

        currentStage = 99;
        terminalArea.setText("");

        try {
            for(int i = 0; i < 3; i++) {
                Toolkit.getDefaultToolkit().beep();
                Thread.sleep(100);
            }
        } catch(Exception ignored){}

        tuxTimer = new Timer(400, e -> updateEasterEggScreen());
        tuxTimer.start();

        currentText = "PROJECT 'FREAX' HISTORY DUMP:\n" +
                "--------------------------------------------------\n" +
                "Линус Торвальдс изначально назвал свой проект FreaX\n" +
                "(Free + Freak + X) и полгода хранил исходники в папке\n" +
                "с этим именем. Но Ари Леммке, администратор FTP-\n" +
                "сервера FUNET, посчитал это имя ужасным и переименовал\n" +
                "каталог в 'Linux' без одобрения самого Линуса!\n" +
                "--------------------------------------------------\n" +
                "Press [F5] to restore primary timeline.";
        charIndex = 0;
        animationTimer.start();
    }

    private void updateEasterEggScreen() {
        tuxFrameIndex = (tuxFrameIndex == 0) ? 1 : 0;
        String[] frame = TUX_FRAMES[tuxFrameIndex];
        String fullPrinted = currentText.substring(0, charIndex);
        String[] textLines = fullPrinted.split("\n");
        StringBuilder sb = new StringBuilder("  [!!!] UNLOCKED SYSTEM EASTER EGG: PROJECT 'FREAX'\n\n");

        for (int i = 0; i < 9; i++) {
            String tuxLine = frame[i];
            sb.append("  ").append(tuxLine);

            // ФИЛИГРАННЫЙ ВЫРАВНИВАТЕЛЬ: жестко добиваем пробелами до ширины в 14 символов
            if (tuxLine.length() < 14) {
                for (int j = 0; j < (14 - tuxLine.length()); j++) {
                    sb.append(" ");
                }
            }

            sb.append("   "); // Фиксированный зазор

            if (i < textLines.length) sb.append(textLines[i]);
            sb.append("\n");
        }
        for (int i = 9; i < textLines.length; i++) {
            sb.append("                     ").append(textLines[i]).append("\n");
        }
        terminalArea.setText(sb.toString());
    }

    private void triggerHistoricalPayload() {
        currentText = "\n\n  [SUCCESS] Floppy boot sector signature 0xAA55 loaded.\n" +
                "  --------------------------------------------------\n" +
                "  HISTORICAL INSIGHT: THE ACADEMY VS THE HOBBYIST\n" +
                "  --------------------------------------------------\n" +
                "  Did you know? Линус Торвальдс писал первую версию \n" +
                "  Linux прямо внутри ОС Minix. Во время разработки \n" +
                "  он случайно перепутал разделы и уничтожил (overwrote)\n" +
                "  свою рабочую систему Minix оригинальными тестами \n" +
                "  будущего ядра Linux! Назад пути не было.\n\n" +
                "  REVEALING ORIGINAL SOURCE COMMENTS (v0.01):\n\n" +
                "  * From: include/linux/sched.h\n" +
                "    /* ... Mentally prepare yourself for the most \n" +
                "     * ugly code you have ever seen. But it works! */\n\n" +
                "  * From: mm/page.c\n" +
                "    /* ... If we run out of memory, we are in deep \n" +
                "     * trouble. Linus hasn't written swap code yet. */\n" +
                "  --------------------------------------------------\n" +
                "  [EMULATION COMPLETE] Linux is ready to rule the world.\n\n" +
                "  >> DO YOU WANT TO VISIT THE ORIGINAL TUHS WEBSITE? [Y/N]: ";
        charIndex = 0;
        animationTimer.start();
    }

    private void handleTextAnimation() {
        if (charIndex < currentText.length()) {
            char c = currentText.charAt(charIndex);
            charIndex++;
            if (currentStage == 99) {
                updateEasterEggScreen();
            } else {
                terminalArea.append(String.valueOf(c));
            }
            animationTimer.setDelay(c == '\n' ? 300 : 12);
        } else {
            animationTimer.stop();
            if (currentStage == 0) {
                currentStage++;
                Timer p = new Timer(600, ev -> executeStage());
                p.setRepeats(false);
                p.start();
            } else if (currentStage == 99) {
                actionButton.setEnabled(true);
                actionButton.setText("F5_BOOT_FLOPPY");
            }
        }
    }

    private JButton createRetroButton(String text) {
        JButton button = new JButton("[" + text + "]");
        button.setFont(new Font(Font.MONOSPACED, Font.BOLD, 11));
        button.setBackground(CRT_BG);
        button.setForeground(PHOSPHOR_DIM);
        button.setFocusPainted(false);
        button.setContentAreaFilled(false);
        button.setBorder(BorderFactory.createEmptyBorder(5, 10, 5, 10));

        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setForeground(PHOSPHOR_BRIGHT);
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setForeground(PHOSPHOR_DIM);
            }
        });
        return button;
    }

    private void openTuhsWeb() {
        if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
            try {
                Desktop.getDesktop().browse(new URI("https://tuhs.org"));
            } catch (Exception ex) {
                terminalArea.append("\n  [ERR] Network error. Visit tuhs.org manually.");
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
                UIManager.put("ScrollPane.background", CRT_BG);
                UIManager.put("ScrollBar.background", CRT_BG);
            } catch(Exception e) {}

            Main app = new Main();
            app.setVisible(true);
        });
    }
}