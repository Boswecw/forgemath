from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExecutionContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LaneSpecPayloadContract(ExecutionContractModel):
    contract_version: str = Field(min_length=1, max_length=64)
    lane_id: str = Field(min_length=1, max_length=255)


class VariableRegistryPayloadContract(ExecutionContractModel):
    variables: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_variables(self) -> "VariableRegistryPayloadContract":
        cleaned = [item.strip() for item in self.variables if item and item.strip()]
        if len(cleaned) != len(self.variables):
            raise ValueError("variables must be non-blank.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("variables must be unique.")
        self.variables = cleaned
        return self


class ThresholdBandContract(ExecutionContractModel):
    label: str = Field(min_length=1, max_length=255)
    min_inclusive: Decimal
    max_exclusive: Decimal | None = None
    max_inclusive: Decimal | None = None

    @model_validator(mode="after")
    def validate_band(self) -> "ThresholdBandContract":
        if (self.max_exclusive is None) == (self.max_inclusive is None):
            raise ValueError("threshold bands require exactly one of max_exclusive or max_inclusive.")
        maximum = self.max_exclusive if self.max_exclusive is not None else self.max_inclusive
        if maximum is None:
            raise ValueError("threshold bands require an upper bound.")
        if self.min_inclusive < 0 or maximum > 1 or self.min_inclusive > maximum:
            raise ValueError("threshold bands must stay within [0,1].")
        return self


class ThresholdSetPayloadContract(ExecutionContractModel):
    bands: list[ThresholdBandContract] = Field(min_length=1)


class VerificationBurdenWeightsContract(ExecutionContractModel):
    w_I: Decimal
    w_V: Decimal
    w_R: Decimal
    w_X: Decimal
    w_D: Decimal
    w_U: Decimal


class VerificationBurdenCapsContract(ExecutionContractModel):
    I_cap: Decimal
    V_cap: Decimal
    R_cap: Decimal
    X_cap: Decimal
    D_cap: Decimal


class VerificationBurdenParameterContract(ExecutionContractModel):
    weights: VerificationBurdenWeightsContract
    caps: VerificationBurdenCapsContract


class RecurrencePressureWeightsContract(ExecutionContractModel):
    w30: Decimal
    w90: Decimal
    wsame: Decimal
    wcross: Decimal
    wpost: Decimal


class RecurrencePressureSaturationContract(ExecutionContractModel):
    k30: Decimal
    k90: Decimal
    ksame: Decimal
    kcross: Decimal
    kpost: Decimal


class RecurrencePressureParameterContract(ExecutionContractModel):
    weights: RecurrencePressureWeightsContract
    saturation: RecurrencePressureSaturationContract


class ExposureFactorCoefficientContract(ExecutionContractModel):
    alpha_pub: Decimal
    alpha_op: Decimal
    alpha_persist: Decimal
    alpha_approve: Decimal
    alpha_cross: Decimal
    alpha_boundary: Decimal


class ExposureFactorParameterContract(ExecutionContractModel):
    coefficients: ExposureFactorCoefficientContract
