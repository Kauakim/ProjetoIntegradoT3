# Importa as bibliotecas necessárias
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import serial
import time


# Inicia a serial
ser = serial.Serial('COM9', 115200, timeout=1)


# Parâmetros importantes do DSP
fs = 750  # Taxa de amostragem (Hz)
t = np.linspace(0, 1, fs, endpoint=False)  # Vetor de tempo (s)
newt = t[50:-50]

# Roda o sistema em looping
while True:
    # Le a serial ate receber "S"
    while True:
        # Lê cada linha da porta serial
        Linha = ser.readline().strip()
        print(Linha)

        if Linha == b'P':
            combined_signal = []

            while True:
                Linha = ser.readline().strip()

                # Verifica se a transmissão foi finalizada a partir do recebimento de "F"
                if Linha == b'F':
                    print("Valores recebidos:", combined_signal)
                    break

                else:
                    try:
                        Valor = int(Linha)
                        combined_signal.append(Valor)
                    except ValueError:
                        pass
                
            break


    # Funções dos filtros que serão aplicados no sinal combinado
    def butter_highpass_filter1(data, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        y = filtfilt(b, a, data)
        return y

    def butter_highpass_filter2(data, cutoff, fs, order=6):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        y = filtfilt(b, a, data)
        return y

    def butter_bandpass_filter1(data, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = filtfilt(b, a, data)
        return y

    def butter_bandpass_filter2(data, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = filtfilt(b, a, data)
        return y
    
    combined_signal = butter_highpass_filter1(combined_signal, 9, fs)
    sinal_15 = butter_bandpass_filter1(combined_signal, 14, 16, fs)
    sinal_45 = butter_bandpass_filter2(combined_signal, 44, 46, fs)
    sinal_70 = butter_highpass_filter2(combined_signal, 65, fs)

    sinal_15 = (sinal_15[50:-50])
    sinal_45 = sinal_45[50:-50]
    sinal_70 = sinal_70[50:-50]


    # Função para calcular o espectro completo do sinal combinado
    def calculate_full_spectrum(signal, fs):
        N = len(signal)
        spectrum = np.abs(fft(signal))[:N // 2]  # Magnitude do espectro
        freqs = fftfreq(N, 1 / fs)[:N // 2]      # Frequências correspondentes
        return freqs, spectrum

    # Calcula o espectro do sinal combinado
    freqs_combined, spectrum_combined = calculate_full_spectrum(combined_signal, fs)

    # Identifica as potências das frequências de interesse
    def find_peak_power(freqs, spectrum, target_freq, tolerance=1):
        # Procura o índice mais próximo da frequência-alvo
        index = np.where((freqs >= target_freq - tolerance) & (freqs <= target_freq + tolerance))[0]
        if len(index) > 0:
            return np.mean(spectrum[index])
        else:
            return 0

    # Calcula as potências para as frequências de interesse
    power_15_crista = find_peak_power(freqs_combined, spectrum_combined, 15)
    power_45_crista = find_peak_power(freqs_combined, spectrum_combined, 45)
    power_70_crista = find_peak_power(freqs_combined, spectrum_combined, 70)
    
    # Exibição das potências
    print(f"Potência da crista de 15 Hz: {power_15_crista:.4f}")
    print(f"Potência da crista de 45 Hz: {power_45_crista:.4f}")
    print(f"Potência da crista de 70 Hz: {power_70_crista:.4f}")


    # Lógica para determinar quais portadoras estão ocupadas
    if power_15_crista > 1500 and power_70_crista > 1500:
        print("Ambas as portadoras ocupadas")
        print("Canal do rádio escolhido: 80")
        ser.write(b'R3')
    elif power_15_crista > 1500:
        print("Portadora de 15 Hz ocupada")
        print("Canal do rádio escolhido: 08")
        ser.write(b'R1')
    elif power_70_crista > 1500:
        print("Portadora de 70 Hz ocupada")
        print("Canal do rádio escolhido: 58")
        ser.write(b'R2')
    else:
        print("Nenhuma das portadoras ocupadas")
        print("Canal do rádio escolhido: 116")
        ser.write(b'R4')

    
    # Plotagem dos sinais combinados e espectros
    plt.figure(figsize=(10, 10))
    
    # Sinal combinado
    plt.subplot(3, 1, 1)
    plt.plot(t, combined_signal, label="Sinal Combinado", color="black")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.legend()

    # Sinais filtrados por portadoras
    plt.subplot(3, 1, 2)
    plt.plot(newt, sinal_15, label="Portadora 15 Hz", color="red")
    plt.plot(newt, sinal_45, label="Portadora 45 Hz", color="green")
    plt.plot(newt, sinal_70, label="Portadora 70 Hz", color="purple")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.legend()

    # Espectro do sinal combinado
    plt.subplot(3, 1, 3)
    plt.plot(freqs_combined, spectrum_combined, label="Espectro do Sinal Combinado", color="blue")
    # Destaque das frequências de interesse
    plt.axvline(15, color="red", linestyle="--", label="15 Hz")
    plt.axvline(45, color="green", linestyle="--", label="45 Hz")
    plt.axvline(70, color="purple", linestyle="--", label="70 Hz")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.grid()
    plt.legend()

    # Ajusta a margem entre os subplots
    plt.subplots_adjust(hspace=0.25)

    # Exibe os gráficos na tela
    plt.tight_layout()    
    plt.show()


    # Aguarda um intervalo antes de reiniciar o loop
    time.sleep(5)