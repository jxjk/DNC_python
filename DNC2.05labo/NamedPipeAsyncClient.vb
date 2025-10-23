Imports System.Threading.Tasks
Imports System.Text
Imports System.IO.Pipes

Public Class NamedPipeAsyncClient

    Private client As New NamedPipeClientStream(".", "NamedPipeTextServer", PipeDirection.InOut, PipeOptions.Asynchronous)
    Private receivedText As String

    Public Event ConnectionChange(ByVal sender As Object, e As EventArgs)
    Public Event ReceivedData(ByVal sender As Object, e As EventArgs)

    Public ReadOnly Property IsConnected As Boolean
        Get
            Return client.IsConnected
        End Get
    End Property

    Public ReadOnly Property Text As String
        Get
            Return Me.receivedText
        End Get
    End Property

    Private Async Sub ConnectAsync()
        Try
            Await client.ConnectAsync

            Do While client.IsConnected

                RaiseEvent ConnectionChange(Me, New EventArgs)

                Dim buffer(255) As Byte
                Await client.ReadAsync(buffer, 0, buffer.Length)

                Me.receivedText = Encoding.Unicode.GetString(buffer)
                RaiseEvent ReceivedData(Me, New EventArgs)
            Loop

            RaiseEvent ConnectionChange(Me, New EventArgs)

        Catch ex As Exception
            MsgBox(ex.ToString())
        End Try
    End Sub

    Private Async Function DeconnectAsync() As Task
        Try
            If client.IsConnected Then

                Dim buffer(0) As Byte : buffer(0) = 1
                Await client.WriteAsync(buffer, 0, buffer.Length)
            End If

            RaiseEvent ConnectionChange(Me, New EventArgs)

        Catch ex As Exception
            MsgBox(ex.ToString())
        End Try
    End Function

    Public Sub Open()
        Call ConnectAsync()
    End Sub

    Public Sub Close()
        Call DeconnectAsync()
        If client IsNot Nothing Then
            client.Close()
        End If
    End Sub

    Protected Overrides Sub Finalize()
        Me.Close()
        MyBase.Finalize()
    End Sub
End Class
