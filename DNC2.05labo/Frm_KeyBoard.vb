Public Class Frm_KeyBoard

    Public txtValue As String = ""
    Public Btn(,) As String = {{"Button1", "1", "!"}, _
                                {"Button2", "2", "^"}, _
                                {"Button3", "3", "#"}, _
                                {"Button4", "4", "$"}, _
                                {"Button5", "5", "%"}, _
                                {"Button6", "6", "&"}, _
                                {"Button7", "7", "'"}, _
                                {"Button8", "8", "("}, _
                                {"Button9", "9", ")"}, _
                                {"Button10", "0", "_"}, _
                                {"Button11", "-", "="}, _
                                {"Button12", "`", "@"}, _
                                {"Button13", "+", ";"}, _
                                {"Button14", ",", "."}, _
                                {"Button15", "}", "]"}, _
                                {"Button16", "{", "["}, _
                                {"ButtonA", "A", "a"}, _
                                {"ButtonB", "B", "b"}, _
                                {"ButtonC", "C", "c"}, _
                                {"ButtonD", "D", "d"}, _
                                {"ButtonE", "E", "e"}, _
                                {"ButtonF", "F", "f"}, _
                                {"ButtonG", "G", "g"}, _
                                {"ButtonH", "H", "h"}, _
                                {"ButtonI", "I", "i"}, _
                                {"ButtonJ", "J", "j"}, _
                                {"ButtonK", "K", "k"}, _
                                {"ButtonL", "L", "l"}, _
                                {"ButtonM", "M", "m"}, _
                                {"ButtonN", "N", "n"}, _
                                {"ButtonO", "O", "o"}, _
                                {"ButtonP", "P", "p"}, _
                                {"ButtonQ", "Q", "q"}, _
                                {"ButtonR", "R", "r"}, _
                                {"ButtonS", "S", "s"}, _
                                {"ButtonT", "T", "t"}, _
                                {"ButtonU", "U", "u"}, _
                                {"ButtonV", "V", "v"}, _
                                {"ButtonW", "W", "w"}, _
                                {"ButtonX", "X", "x"}, _
                                {"ButtonY", "Y", "y"}, _
                                {"ButtonZ", "Z", "z"}, _
                                {"ButtonSP", "Space", "Space"}}

    Private Cap As Boolean = True

    '起動時実行
    Private Sub Frm_KeyBoard_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        'Me.Text = Form1.Tenkeymode          'ウインドーバーにモード設定変数を表示
        'フォームサイズ変更不可
        Me.FormBorderStyle = FormBorderStyle.FixedSingle
        'フォーム最大化不可
        Me.MaximizeBox = Not Me.MaximizeBox
        ChangeBtnText()

        'InputValue.MaxLength = 38

        'フォームサイズをフルスクリーン*0.8へ変更
        changeFormSize(80)

        '150901 hishiki main以外の画面（keyboard,input,info）の表示位置変更 -start-
        'フォームをメインフォームの中央に配置
        'Dim bufX, bufY As Integer
        'bufX = Frm_main.Location.X + (Frm_main.Width - Me.Width) / 2
        'bufY = Frm_main.Location.Y + (Frm_main.Height - Me.Height) / 2
        'Me.Location = New Point(bufX, bufY)

        'フォームをディスプレイの中央に配置
        'ディスプレイの幅
        Dim w As Integer = System.Windows.Forms.Screen.PrimaryScreen.Bounds.Width
        'ディスプレイの高さ
        Dim h As Integer = System.Windows.Forms.Screen.PrimaryScreen.Bounds.Height

        Dim bufX, bufY As Integer
        bufX = (w - Me.Width) / 2
        bufY = (h - Me.Height) / 2
        Me.Location = New Point(bufX, bufY)

        '150901 hishiki main以外の画面（keyboard,input,info）の表示位置変更 -end-


    End Sub

    Private Sub BtnClick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles _
      Button1.Click, Button2.Click, Button3.Click, Button4.Click, Button5.Click, Button6.Click, Button7.Click, Button8.Click _
    , Button9.Click, Button10.Click, Button11.Click, Button12.Click, Button13.Click, Button14.Click, Button15.Click, Button16.Click _
    , ButtonA.Click, ButtonB.Click, ButtonC.Click, ButtonD.Click, ButtonE.Click, ButtonF.Click, ButtonG.Click, ButtonH.Click, ButtonI.Click _
    , ButtonJ.Click, ButtonK.Click, ButtonL.Click, ButtonM.Click, ButtonN.Click, ButtonO.Click, ButtonP.Click, ButtonQ.Click, ButtonR.Click _
    , ButtonS.Click, ButtonT.Click, ButtonU.Click, ButtonV.Click, ButtonW.Click, ButtonX.Click, ButtonY.Click, ButtonZ.Click, ButtonSP.Click

        Dim Button = TryCast(sender, Button)
        For i As Integer = 0 To UBound(Btn)
            If Button.Name = Btn(i, 0) Then
                Dim addStr As String = ""
                If Button.Name = "ButtonSP" Then
                    addStr = " "
                Else
                    If Cap = True Then
                        addStr = Btn(i, 1)
                    Else
                        addStr = Btn(i, 2)
                    End If
                End If

                InputValue.Text = InputValue.Text & addStr
                txtValue = txtValue & addStr
                Exit For
            End If
        Next

    End Sub

    Private Sub ChangeBtnText()
        For i As Integer = 0 To UBound(Btn)
            '配置されたコントロールの中から対象Buttonを検索
            Dim targetBTN As Button
            Dim btnName As String = Btn(i, 0)
            Dim c As Control() = Me.Controls.Find(btnName, True)
            If c.Length = 1 Then
                targetBTN = c(0)
                targetBTN.UseMnemonic = False '「&」が表示されない問題対応
            Else
                Exit Sub
            End If

            Dim btnText As String = ""
            If Cap = True Then
                btnText = Btn(i, 1)
            Else
                btnText = Btn(i, 2)
            End If
            targetBTN.Text = btnText

        Next
    End Sub

    'CapsLock
    Private Sub ButtonCAP_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ButtonCAP.Click

        If Cap = True Then
            ButtonCAP.BackColor = SystemColors.ControlLight '色変更
            CapsLB.Enabled = False                          'Lock表示
            ABCLB.Text = "abc･･･"                           'サンプル表示
            Cap = False
        Else
            ButtonCAP.BackColor = SystemColors.ControlDark  '色変更
            CapsLB.Enabled = True                           'Lock表示
            ABCLB.Text = "ABC･･･"                           'サンプル表示
            Cap = True
        End If

        changeBtnText()

    End Sub

    'クローズ
    Private Sub ButtonCAN_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ButtonCAN.Click
        InputValue.Text = ""
        Me.Close()
    End Sub

    'BS
    Private Sub ButtonBS_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ButtonBS.Click
        If InputValue.Text.Length > 0 Then
            InputValue.Text = InputValue.Text.Substring(0, InputValue.Text.Length - 1)
            txtValue = txtValue.Substring(0, txtValue.Length - 1)
        End If
    End Sub

    'CLR
    Private Sub ButtonCLR_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ButtonCLR.Click
        InputValue.Text = ""
        txtValue = ""
    End Sub

    'Enter
    Private Sub ButtonENT_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ButtonENT.Click
        'キーボード内のテキストボックスの値をTB_Modelへ反映。
        If InputValue.TextLength > 0 Then
            If txtValue.Length = 0 Then
                txtValue = InputValue.Text
            End If
            Frm_main.SearchTB_Model(txtValue)
        End If
        Me.Close()                          'このフォームを閉じる
    End Sub

    'フォーム表示後
    Private Sub ABCKey_Shown(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Shown
        '画面表示リフレッシュ
        Me.Refresh()
    End Sub

    'キーボードフォームクローズ時のイベント
    Private Sub Frm_KeyBoard_FormClosed(sender As System.Object, e As System.Windows.Forms.FormClosedEventArgs) Handles MyBase.FormClosed
        Frm_main.TB_Barcode.Focus()
    End Sub

    Private Sub InputValue_TextChanged(sender As System.Object, e As System.EventArgs) Handles InputValue.TextChanged
        If InputValue.Text.Length > InputValue.MaxLength Then
            InputValue.Text = InputValue.Text.Substring(1) 'テキストボックス内の文字において、先頭1文字削除
        End If
    End Sub

    'フォームのサイズを使用PCの画面サイズにあわせて変更 引数：フルスクリーンに対するパーセント（フルスクリーンの場合100を指定）
    Private Sub changeFormSize(ByVal ratio As Integer)

        'デフォルトのフォーム1の縦横比取得
        Dim defRatioW_H As Single = ToHalfAdjust(Me.Width / Me.Height, 2)

        'フォーム上のコントロールを取得し、それぞれのW,H,X,Yの値を保持
        Dim all As Control() = GetAllControls(Me)
        Dim cntrl_Frm(all.Length - 1) As Control
        Dim Wratio_Frm(all.Length - 1) As Single
        Dim Hratio_Frm(all.Length - 1) As Single
        Dim Xratio_Frm(all.Length - 1) As Single
        Dim Yratio_Frm(all.Length - 1) As Single

        '現在のフォームの位置、縦横比を取得
        Dim i As Integer = 0
        For Each c As Control In all '比率を設定
            cntrl_Frm(i) = c
            Wratio_Frm(i) = c.Width / ClientSize.Width
            Hratio_Frm(i) = c.Height / ClientSize.Height
            Xratio_Frm(i) = c.Location.X / ClientSize.Width
            Yratio_Frm(i) = c.Location.Y / ClientSize.Height
            i = i + 1
        Next

        '使用PCのモニターの縦横比を取得
        Dim screenRacioW_H As Single = ToHalfAdjust(Screen.GetWorkingArea(Me).Width / Screen.GetWorkingArea(Me).Height, 2)

        'フォームサイズを使用環境に合わせてフルスクリーンへ変更
        '使用するモニターの縦横比に応じて、メイン画面のサイズ設定
        If screenRacioW_H >= defRatioW_H Then 'デフォルトのメイン画面の縦横比に対してモニターが横長の場合

            Me.Height = Screen.GetWorkingArea(Me).Height * ratio / 100 '縦方向のサイズをモニターのサイズに合わせる
            Me.Width = Me.Height * defRatioW_H '横方向は、設定した高さ×デフォルト縦横比

        Else
            Me.Width = Screen.GetWorkingArea(Me).Width * ratio / 100 '横方向のサイズをモニターのサイズに合わせる
            Me.Height = Me.Width / defRatioW_H '縦方向は、設定した幅/デフォルト縦横比
        End If

        '初期の位置関係、サイズ比率を保持したまま画面サイズにあわせてコントロールの位置およびサイズ変更
        Dim ControllerPosition As Point = New Point()
        Dim j As Integer = 0
        For j = 0 To cntrl_Frm.Length - 1
            cntrl_Frm(j).Width = Wratio_Frm(j) * ClientSize.Width
            cntrl_Frm(j).Height = Hratio_Frm(j) * ClientSize.Height
            ControllerPosition.X = Xratio_Frm(j) * ClientSize.Width
            ControllerPosition.Y = Yratio_Frm(j) * ClientSize.Height
            cntrl_Frm(j).Location = ControllerPosition
        Next

    End Sub

    'フォーム上のコントロールを取得
    Public Function GetAllControls(ByVal top As Control) As Control()
        Dim buf As ArrayList = New ArrayList
        For Each c As Control In top.Controls
            buf.Add(c)
            buf.AddRange(GetAllControls(c))
        Next
        Return CType(buf.ToArray(GetType(Control)), Control())
    End Function

    '引数で指定した精度の数値に四捨五入した値を返却
    Public Function ToHalfAdjust(ByVal dValue As Double, ByVal iDigits As Integer) As Single
        Dim dCoef As Single = System.Math.Pow(10, iDigits)

        If dValue > 0 Then
            Return System.Math.Floor((dValue * dCoef) + 0.5) / dCoef
        Else
            Return System.Math.Ceiling((dValue * dCoef) - 0.5) / dCoef
        End If
    End Function

End Class