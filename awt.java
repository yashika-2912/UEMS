import java.awt.*;
import java.awt.event.*;

public class awt extends Frame implements ActionListener {
    awt() {
        Button b = newButton("click me");
        Label l = new Label("awt ");
        add(b);
        add(l);
        b.addActionListener(this);
        setLayout(new FlowLayout());
        setSize(300, 400);
        setVisible(true);
    }

    public void actionPerformed(ActionEvent e) {
        l.setText("button clicked");
    }

    public static void main(String args[]) {
        new awt();
    }
}
