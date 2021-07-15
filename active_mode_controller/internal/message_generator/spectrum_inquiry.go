package message_generator

import "github.com/domain-proxy/active_move_controller/api/active_mode"

const (
	// TODO make this configurable
	lowestFrequencyHz  int64 = 3550 * 1e6
	highestFrequencyHz int64 = 3700 * 1e6
)

type spectrumInquiryRequest struct {
	CbsdId           string          `json:"cbsdId"`
	InquiredSpectrum *frequencyRange `json:"inquiredSpectrum"`
}

func (*spectrumInquiryRequest) name() string {
	return "spectrumInquiry"
}

type frequencyRange struct {
	LowFrequency  int64 `json:"lowFrequency"`
	HighFrequency int64 `json:"highFrequency"`
}

type spectrumInquiryMessageGenerator struct{}

func (*spectrumInquiryMessageGenerator) generateMessages(config *active_mode.ActiveModeConfig) []message {
	req := &spectrumInquiryRequest{
		CbsdId: config.GetCbsd().GetId(),
		InquiredSpectrum: &frequencyRange{
			LowFrequency:  lowestFrequencyHz,
			HighFrequency: highestFrequencyHz,
		},
	}
	return []message{req}
}
