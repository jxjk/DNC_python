Public Class Frm_Calc

    Private Sub Frm_Calc_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

        Try '150928 hishiki try追加

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

            Me.Text = Frm_main.targetLBL.Text

            'フォームサイズ変更不可
            Me.FormBorderStyle = FormBorderStyle.FixedSingle
            'フォーム最大化不可
            Me.MaximizeBox = Not Me.MaximizeBox

        Catch ex As Exception
            Frm_main.Logger.Warn(ex.ToString)
        End Try

    End Sub

    'キャンセル
    Private Sub Button11_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button11.Click
        Me.Close()
    End Sub

    '150915 hishiki 計算機バグ対応　-start- 0から9までのイベントを1つに集約
    Private Sub Button0to9_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button0.Click, Button1.Click, Button2.Click, _
        Button3.Click, Button4.Click, Button5.Click, Button6.Click, Button7.Click, Button8.Click, Button9.Click

        Try '150928 hishiki try追加

            '0*入力禁止(0.*はOK)
            If TB_InputValue.Text = "0" Or TB_InputValue.Text = "-0" Then
                Exit Sub
            End If

            'senderのtextから数字を取得し、全角から半角へ変換
            Dim TB As Button = CType(sender, Button)
            Dim tmpValue As String = TB.Text
            'tmpValue = StrConv(tmpValue, VbStrConv.Narrow)　'150928 hishiki 電卓バグ修正　全角→半角修正は外国語OSではNGみたいなので、ボタンのテキストを半角にして対応

            '小数点以下の文字数を取得（小数点なしの場合-1返却）
            Dim decimalValueLen As Integer = getDecimalValueLength()

            '整数部を5桁（マイナスがある場合6桁）、小数点以下3桁まで入力可能に
            '→160805 hishiki input系の整数部の桁数をini.csvで可変にできるように修正
            '→160805 hishiki 小数点以下桁数をini.csvで可変にできるように修正
            If decimalValueLen < 0 Then
                '160805 hishiki start input系の整数部の桁数をini.csvで可変にできるように修正
                Dim maxlen As Integer = Frm_main.NumberOfDigit
                'Dim maxlen As Integer = 5
                '160805 hishiki end
                If TB_InputValue.Text.Contains("-") Then
                    maxlen = maxlen + 1
                End If
                If TB_InputValue.Text.Length < maxlen Then
                    TB_InputValue.Text = TB_InputValue.Text & tmpValue
                End If
                '160805 hishiki start 小数点以下桁数をini.csvで可変にできるように修正
            ElseIf 0 <= decimalValueLen And decimalValueLen < Frm_main.DecimalPlace Then
                'ElseIf 0 <= decimalValueLen And decimalValueLen < 3 Then
                '160805 hishiki end
                TB_InputValue.Text = TB_InputValue.Text & tmpValue
            End If

        Catch ex As Exception
            Frm_main.Logger.Warn(ex.ToString)
        End Try

    End Sub
    '150915 hishiki　計算機バグ対応 -end-

    '「.」
    Private Sub Button100_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button100.Click
        '150915 hishki　計算機バグ対応 -start-
        If TB_InputValue.Text = "" Or TB_InputValue.Text = "-" Then
            Exit Sub
        End If
        '150915 hishki　計算機バグ対応 -end-

        TB_InputValue.Text = TB_InputValue.Text & "."
        Button100.Enabled = False
    End Sub
    '「C」
    Private Sub CB_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CB.Click
        TB_InputValue.Text = ""
        Button100.Enabled = True
        Frm_Calc_Load(Nothing, Nothing)
    End Sub
    '「BS」
    Private Sub BSB_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles BSB.Click
        '151008 hishiki
        If TB_InputValue.Text = "" Then
            Exit Sub
        End If
        If TB_InputValue.Text.Substring(TB_InputValue.Text.Length - 1) = "." Then
            Button100.Enabled = True
        End If
        TB_InputValue.Text = TB_InputValue.Text.Substring(0, TB_InputValue.Text.Length - 1)
    End Sub

    Private Sub Button10_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button10.Click
        If TB_InputValue.Text <> "" Then
            Frm_main.targetTB.Text = TB_InputValue.Text

            '151006 hishiki 入力値により、テキストボックスの幅を変更
            'テキストボックス及びテーブルレイアウトパネルの幅を再設定
            Dim defaultWidth As Integer = TextRenderer.MeasureText(New String("0", Frm_main.targetTB.MaxLength), Frm_main.targetTB.Font).Width '半角数字のサイズ×最大文字数でwidth設定
            Dim wdt As Integer = TextRenderer.MeasureText(New String("0", Frm_main.LenB(Frm_main.targetTB.Text)), Frm_main.targetTB.Font).Width '半角のサイズ×最大文字数でwidth設定
            If wdt > defaultWidth Then
                Frm_main.targetTB.Width = wdt 'ターゲットのTBの幅を変更
                Dim defTLPWidth As Integer = Frm_main.targetTLP.Width
                Frm_main.targetTLP.Width = defTLPWidth + (wdt - defaultWidth) 'テーブルレイアウトパネルの幅をTBの幅増分だけ追加

            Else
                Frm_main.targetTB.Width = defaultWidth
            End If

        End If

        Me.Close()
    End Sub
    '""，0の場合はEnterを表示しない　何か入力された後は有効にする
    Private Sub InputValue_TextChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles TB_InputValue.TextChanged
        Button10.Enabled = True
        If TB_InputValue.Text = "" Then
            BSB.Enabled = False
        Else
            BSB.Enabled = True
        End If
    End Sub

    '-符号
    Private Sub PNB_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles PNB.Click
        TB_InputValue.Text = "-"
        '150915 hishki　計算機バグ対応 -start- 「.」ボタン復活
        Button100.Enabled = True
        '150915 hishki　計算機バグ対応 -end-
    End Sub

    'フォーム表示後
    Private Sub TenKey_Shown(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Shown
        '画面表示リフレッシュ
        Me.Refresh()
    End Sub

    Private Sub Frm_Calc_FormClosed(sender As System.Object, e As System.Windows.Forms.FormClosedEventArgs) Handles MyBase.FormClosed
        Frm_main.TB_Barcode.Focus()
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

    '入力値の小数点以下の桁数を返却する関数
    Private Function getDecimalValueLength()
        Dim i As Integer = TB_InputValue.Text.IndexOf(".")
        Dim decimalValueLen As Integer = i
        If i > 0 Then
            Dim decimalValue As String = TB_InputValue.Text.Substring(i + 1, TB_InputValue.Text.Length - i - 1)
            decimalValueLen = decimalValue.Length
        End If

        Return decimalValueLen
    End Function


    ''「0」
    'Private Sub Button0_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button0.Click

    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "0"
    '    End If

    'End Sub
    ''「1」
    'Private Sub Button1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button1.Click

    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "1"
    '    End If

    'End Sub
    ''「2」
    'Private Sub Button2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button2.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "2"
    '    End If
    'End Sub
    ''「3」
    'Private Sub Button3_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button3.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "3"
    '    End If
    'End Sub
    ''「4」
    'Private Sub Button4_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button4.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "4"
    '    End If
    'End Sub
    ''「5」
    'Private Sub Button5_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button5.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "5"
    '    End If
    'End Sub
    ''「6」
    'Private Sub Button6_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button6.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "6"
    '    End If
    'End Sub
    ''「7」
    'Private Sub Button7_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button7.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "7"
    '    End If
    'End Sub
    ''「8」
    'Private Sub Button8_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button8.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "8"
    '    End If
    'End Sub
    ''「9」
    'Private Sub Button9_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button9.Click
    '    If TB_InputValue.Text.Length < 6 Then
    '        TB_InputValue.Text = TB_InputValue.Text & "9"
    '    End If
    'End Sub

End Class