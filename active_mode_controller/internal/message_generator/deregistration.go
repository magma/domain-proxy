package message_generator

import "github.com/domain-proxy/active_move_controller/api/active_mode"

type deregistrationMessageGenerator struct{}

func (*deregistrationMessageGenerator) generateMessages(config *active_mode.ActiveModeConfig) []message {
	req := &DeregistrationRequest{
		CbsdId: config.GetCbsd().GetId(),
	}
	return []message{req}
}

type DeregistrationRequest struct {
	CbsdId string `json:"cbsdId"`
}

func (*DeregistrationRequest) name() string {
	return "deregistration"
}
