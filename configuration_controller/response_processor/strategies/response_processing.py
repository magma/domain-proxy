import logging
from typing import List

from db_service.models import DBGrant, DBGrantState, DBResponse
from db_service.session_manager import Session
from mappings.types import GrantStates, ResponseCodes

logger = logging.getLogger(__name__)


CBSD_ID = "cbsdId"
GRANT_ID = "grantId"
GRANT_EXPIRE_TIME = "grantExpireTime"
HEARTBEAT_INTERVAL = "heartbeatInterval"
TRANSMIT_EXPIRE_TIME = "transmitExpireTime"
CHANNEL_TYPE = "channelType"


def process_registration_responses(responses: List[DBResponse], session: Session) -> None:
    for response in responses:
        if response.response_code == ResponseCodes.DEREGISTER.value:
            _terminate_all_grants_from_response(response, session)
            return


def process_spectrum_inquiry_responses(responses: List[DBResponse], session: Session) -> None:
    for response in responses:
        if response.response_code == ResponseCodes.DEREGISTER.value:
            _terminate_all_grants_from_response(response, session)
            return


def process_grant_responses(responses: List[DBResponse], session: Session) -> None:
    grant_idle_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.IDLE.value).scalar()
    grant_granted_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.GRANTED.value).scalar()
    for response in responses:
        grant = _get_or_create_grant_from_response(response, session)
        _update_grant_from_response(response, grant)

        # Grant response codes worth considering here also are:
        # 400 - INTERFERENCE
        # 401 - GRANT_CONFLICT
        # Might need better processing, for now we set the state to IDLE in all cases other than 0
        if response.response_code == ResponseCodes.SUCCESS.value:
            new_state = grant_granted_state
        else:
            new_state = grant_idle_state
        logger.info(f'process_grant_responses: Updating grant state from {grant.state} to {new_state}')
        grant.state = new_state
    return


def process_heartbeat_responses(responses: List[DBResponse], session: Session) -> None:
    grant_idle_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.IDLE.value).scalar()
    grant_granted_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.GRANTED.value).scalar()
    grant_authorized_state = session.query(DBGrantState).filter(
        DBGrantState.name == GrantStates.AUTHORIZED.value).scalar()
    for response in responses:
        grant = _get_or_create_grant_from_response(response, session)
        logger.info(f'Processing grant: {grant}')
        _update_grant_from_response(response, grant)

        if response.response_code == ResponseCodes.SUCCESS.value:
            new_state = grant_authorized_state
        elif response.response_code == ResponseCodes.SUSPENDED_GRANT.value:
            new_state = grant_granted_state
        elif response.response_code in [ResponseCodes.TERMINATED_GRANT.value, ResponseCodes.UNSYNC_OP_PARAM.value]:
            new_state = grant_idle_state
        elif response.response_code == ResponseCodes.DEREGISTER.value:
            _terminate_all_grants_from_response(response, session)
            return
        else:
            new_state = grant.state
        logger.info(f'process_heartbeat_responses: Updating grant state from {grant.state} to {new_state}')
        grant.state = new_state
    return


def process_relinquishment_responses(responses: List[DBResponse], session: Session) -> None:
    grant_idle_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.IDLE.value).scalar()
    for response in responses:
        grant = _get_or_create_grant_from_response(response, session)
        _update_grant_from_response(response, grant)

        if response.response_code == ResponseCodes.SUCCESS.value:
            new_state = grant_idle_state
        elif response.response_code == ResponseCodes.DEREGISTER.value:
            _terminate_all_grants_from_response(response, session)
            return
        else:
            new_state = grant.state
        logger.info(f'process_relinquishment_responses: Updating grant state from {grant.state} to {new_state}')
        grant.state = new_state
    return


def process_deregistration_responses(responses: List[DBResponse], session: Session) -> None:
    for response in responses:
        if response.response_code in [ResponseCodes.SUCCESS.value, ResponseCodes.DEREGISTER.value]:
            _terminate_all_grants_from_response(response, session)
            return


def _get_or_create_grant_from_response(response: DBResponse, session: Session) -> None:
    cbsd_id = response.payload[CBSD_ID]
    grant_id = response.payload[GRANT_ID]
    logger.info(f'Getting grant by cbsd_id={cbsd_id} and grant_id={grant_id}')
    grant = session.query(DBGrant).filter(DBGrant.cbsd_id == cbsd_id, DBGrant.grant_id == grant_id).scalar()

    if not grant:
        grant_idle_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.IDLE.value).scalar()
        grant = DBGrant(cbsd_id=cbsd_id, grant_id=grant_id, state=grant_idle_state)
        session.add(grant)
        logger.info(f'Created new grant: {grant}')
    return grant


def _update_grant_from_response(response: DBResponse, grant: DBGrant) -> None:
    grant_expire_time = response.payload.get(GRANT_EXPIRE_TIME, None)
    heartbeat_interval = response.payload.get(HEARTBEAT_INTERVAL, None)
    transmit_expire_time = response.payload.get(TRANSMIT_EXPIRE_TIME, None)
    channel_type = response.payload.get(CHANNEL_TYPE, None)
    if grant_expire_time:
        grant.grant_expire_time = grant_expire_time
    if heartbeat_interval:
        grant.heartbeat_interval = int(heartbeat_interval)
    if transmit_expire_time:
        grant.transmit_expire_time = transmit_expire_time
    if channel_type:
        grant.channel_type = channel_type
    grant.responses.append(response)
    logger.info(f'Updated grant: {grant}')


def _terminate_all_grants_from_response(response: DBResponse, session: Session) -> None:
    cbsd_id = response.payload[CBSD_ID]
    logger.info(f'Terminating all grants for cbsd_id: {cbsd_id}')
    grant_idle_state = session.query(DBGrantState).filter(DBGrantState.name == GrantStates.IDLE.value).scalar()
    for grant in session.query(DBGrant).filter(DBGrant.cbsd_id == cbsd_id).all():
        logger.info(f'Terminating grant {grant}')
        grant.state = grant_idle_state
